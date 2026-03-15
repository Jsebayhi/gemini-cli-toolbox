import json
import subprocess
import logging
import os
from typing import Dict, Any
from app.models.session import GeminiSession
from app.services.base import DiscoveryProvider

logger = logging.getLogger(__name__)

class TailscaleService(DiscoveryProvider):
    """Session Provider for remote Tailscale nodes."""

    def is_available(self) -> bool:
        """Checks if Tailscale is running."""
        socket_path = "/run/tailscale/tailscaled.sock"
        return os.path.exists(socket_path)

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Executes `tailscale status --json`."""
        socket_path = "/run/tailscale/tailscaled.sock"
        if not os.path.exists(socket_path):
            return {}

        try:
            cmd = ["tailscale", f"--socket={socket_path}", "status", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return {}
                
            return json.loads(result.stdout)
        except Exception:
            return {}

    def get_sessions(self) -> Dict[str, GeminiSession]:
        """Returns GeminiSession objects for all nodes in Tailnet."""
        sessions = {}
        status = TailscaleService.get_status()
        peers = status.get("Peer", {})
        
        for _, node in peers.items():
            hostname = node.get("HostName", "")
            if not hostname.startswith("gem-"):
                continue

            addrs = node.get("TailscaleIPs", [])
            ip = next((a for a in addrs if "." in a), None)
            
            if not ip:
                continue

            session = GeminiSession.from_name(hostname)
            if not session:
                continue
            
            session.ip = ip
            session.is_reachable = node.get("Online", False)
            
            sessions[hostname] = session
                    
        return sessions
