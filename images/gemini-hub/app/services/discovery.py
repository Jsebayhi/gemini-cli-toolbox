import json
import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DiscoveryService:
    """Manages discovery of local and remote Gemini sessions."""

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Executes `tailscale status --json`."""
        # Check if tailscaled is even running before trying
        try:
            # We check if the tailscale command exists and can talk to the daemon
            cmd = ["tailscale", "status", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode != 0:
                return {}
                
            return json.loads(result.stdout)
        except Exception:
            return {}

    @staticmethod
    def get_local_containers() -> List[Dict[str, Any]]:
        """
        Queries 'docker ps' for all gem-* containers and returns their basic info.
        """
        try:
            # Format: Name|Ports|Status
            cmd = ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}|{{.Status}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode != 0:
                return []

            containers = []
            for line in result.stdout.strip().split('\n'):
                if not line or "|" not in line:
                    continue
                
                name, ports_str, status_str = line.split('|', 2)
                if not name.startswith("gem-"):
                    continue
                
                # Parse Hostname Metadata: gem-{project}-{type}-{suffix}
                parts = [p for p in name.split('-') if p]
                project = "Unknown"
                session_type = "Unknown"
                uid = "Unknown"
                
                if len(parts) >= 4:
                    session_type = parts[-2]
                    project = "-".join(parts[1:-2])
                    uid = parts[-1]
                elif len(parts) == 3:
                    project = parts[1]
                    session_type = "cli"
                    uid = parts[-1]

                local_url = None
                # Parse ports for 3000 mapping
                for part in ports_str.split(','):
                    part = part.strip()
                    if "->3000/tcp" in part:
                        left = part.split("->")[0]
                        if ":" in left:
                            host_port = left.split(":")[-1]
                            local_url = f"http://localhost:{host_port}"
                            break

                containers.append({
                    "name": name,
                    "project": project,
                    "type": session_type,
                    "uid": uid,
                    "local_url": local_url,
                    "online": "Up" in status_str
                })
            return containers
        except Exception as e:
            logger.error(f"Error getting docker containers: {e}")
            return []

    @staticmethod
    def parse_peers(status_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Unifies local Docker containers and Tailscale peers."""
        local_containers = DiscoveryService.get_local_containers()
        peers = status_json.get("Peer", {})
        
        # Create a map of Tailscale peers by HostName for quick lookup
        ts_map = {}
        for _, node in peers.items():
            hostname = node.get("HostName", "")
            if hostname.startswith("gem-"):
                addrs = node.get("TailscaleIPs", [])
                ip = next((a for a in addrs if "." in a), None)
                ts_map[hostname] = {
                    "ip": ip,
                    "online": node.get("Online", False)
                }

        machines = []
        # Process Local Containers (Primary Source)
        seen_hostnames = set()
        for container in local_containers:
            hostname = container["name"]
            seen_hostnames.add(hostname)
            
            ts_info = ts_map.get(hostname)
            machines.append({
                "name": hostname,
                "project": container["project"],
                "type": container["type"],
                "uid": container["uid"],
                "ip": ts_info["ip"] if ts_info else "127.0.0.1",
                "online": container["online"],
                "local_url": container["local_url"],
                "is_local": True,
                "has_vpn": ts_info is not None
            })

        # Process remaining Tailscale Peers (Remote nodes not on this host)
        for hostname, ts_info in ts_map.items():
            if hostname not in seen_hostnames:
                # This is a remote session on another machine
                raw_parts = hostname.split('-')
                parts = [p for p in raw_parts if p]
                
                project = "Unknown"
                session_type = "Unknown"
                uid = "Unknown"
                
                if len(parts) >= 4:
                    session_type = parts[-2]
                    project = "-".join(parts[1:-2])
                    uid = parts[-1]
                
                machines.append({
                    "name": hostname,
                    "project": project,
                    "type": session_type,
                    "uid": uid,
                    "ip": ts_info["ip"],
                    "online": ts_info["online"],
                    "local_url": None,
                    "is_local": False,
                    "has_vpn": True
                })
                
        machines.sort(key=lambda x: x["name"])
        return machines
