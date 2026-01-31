import json
import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TailscaleService:
    """Manages interactions with the Tailscale daemon."""

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Executes `tailscale status --json`."""
        try:
            cmd = ["tailscale", "status", "--json"]
            # Timeout added for safety
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                logger.error(f"Tailscale error: {result.stderr}")
                return {}
                
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            logger.error("Tailscale status command timed out")
            return {}
        except Exception as e:
            logger.error(f"Exception querying tailscale: {e}")
            return {}

    @staticmethod
    def get_local_ports() -> Dict[str, str]:
        """
        Returns a mapping of {container_name: local_url} for gemini containers
        that have port 3000 exposed to the host.
        """
        try:
            # We use "docker ps" to find containers that map port 3000.
            # Format: Name|Ports
            # Example Ports: "127.0.0.1:32768->3000/tcp"
            cmd = ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode != 0:
                return {}

            mapping = {}
            for line in result.stdout.strip().split('\n'):
                if not line or "|" not in line:
                    continue
                
                name, ports_str = line.split('|', 1)
                if not name.startswith("gem-"):
                    continue
                
                # Parse ports
                for part in ports_str.split(','):
                    part = part.strip()
                    if "->3000/tcp" in part:
                        # Extract "127.0.0.1:32768" from "127.0.0.1:32768->3000/tcp"
                        left = part.split("->")[0]
                        if ":" in left:
                            host_port = left.split(":")[-1]
                            mapping[name] = f"http://localhost:{host_port}"
                            break
            return mapping
        except Exception as e:
            logger.error(f"Error getting docker ports: {e}")
            return {}

    @staticmethod
    def parse_peers(status_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts and filters Gemini peers from status JSON."""
        machines = []
        peers = status_json.get("Peer", {})
        local_ports = TailscaleService.get_local_ports()
        
        for _, node in peers.items():
            hostname = node.get("HostName", "")
            
            # FILTER: Only show "gem-" instances
            if not hostname.startswith("gem-"):
                continue
                
            # Parse Hostname Metadata: gem-{project}-{type}-{suffix}
            raw_parts = hostname.split('-')
            parts = [p for p in raw_parts if p]
            
            project = "Unknown"
            session_type = "Unknown"
            
            if len(parts) >= 4:
                session_type = parts[-2]
                project = "-".join(parts[1:-2])
            elif len(parts) == 3:
                project = parts[1]
                session_type = "cli"
                
            addrs = node.get("TailscaleIPs", [])
            ip = next((a for a in addrs if "." in a), None)
            
            if ip:
                machines.append({
                    "name": hostname,
                    "project": project,
                    "type": session_type,
                    "ip": ip,
                    "online": node.get("Online", False),
                    "local_url": local_ports.get(hostname)
                })
                
        machines.sort(key=lambda x: x["name"])
        return machines
