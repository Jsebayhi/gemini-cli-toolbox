import json
import subprocess
import logging
import os
from typing import Dict, Any
from app.models.session import GeminiSession
from app.services.base import DiscoveryProvider

logger = logging.getLogger(__name__)

class TailscaleService(DiscoveryProvider):
    """Provider that discovers peers via Tailscale status in a sidecar."""

    def __init__(self):
        self.container_name = os.environ.get("GEMINI_HUB_CONTAINER_NAME", "gemini-hub-service")
        self.sidecar_name = f"{self.container_name}-vpn"

    def is_available(self) -> bool:
        """Checks if the VPN sidecar is running."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", self.sidecar_name],
                capture_output=True, text=True, timeout=2
            )
            return result.stdout.strip() == "true"
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Executes `tailscale status --json` inside the sidecar."""
        try:
            cmd = ["docker", "exec", self.sidecar_name, "tailscale", "status", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                return {}

            return json.loads(result.stdout)
        except Exception:
            return {}

    def get_sessions(self) -> Dict[str, GeminiSession]:
        """Returns GeminiSession objects for all nodes in Tailnet."""
        sessions = {}
        status = self.get_status()
        peers = status.get("Peer", {})
        
        for _, node in peers.items():
            hostname = node.get("HostName", "")
            if not hostname.startswith("gem-"):
                continue
            
            # Extract basic info
            # Format: gem-{PROJECT}-{TYPE}-{ID}
            try:
                parts = hostname.split("-")
                project = "-".join(parts[1:-2])
                session_type = parts[-2]
                session_id = parts[-1]
            except (ValueError, IndexError):
                continue

            # Standard Tailscale logic
            ip = node.get("TailscaleIPs", [""])[0]
            
            session = GeminiSession(hostname, project, session_type, session_id)
            if not session:
                continue
            
            session.ip = ip
            session.is_reachable = node.get("Online", False)
            
            sessions[hostname] = session
                    
        return sessions
