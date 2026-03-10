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
            # We use the FHS-compliant socket path
            cmd = ["tailscale", "--socket=/run/tailscale/tailscaled.sock", "status", "--json"]
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
        """Extracts and filters Gemini peers from status JSON and local docker containers."""
        machines_dict = {} # Primary session name -> data
        peers = status_json.get("Peer", {})
        local_ports = TailscaleService.get_local_ports()

        def extract_metadata(hostname: str) -> Dict[str, Any]:
            # Handle sidecar suffixes first
            is_vpn = hostname.endswith("-vpn")
            is_lan = hostname.endswith("-lan")
            
            clean_name = hostname
            if is_vpn: clean_name = hostname[:-4]
            if is_lan: clean_name = hostname[:-4]
            
            # Parse Hostname Metadata: gem-{project}-{type}-{suffix}
            raw_parts = clean_name.split('-')
            parts = [p for p in raw_parts if p]
            
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
            return {
                "project": project, 
                "type": session_type, 
                "uid": uid, 
                "is_sidecar": is_vpn or is_lan, 
                "parent": clean_name,
                "sidecar_type": "vpn" if is_vpn else ("lan" if is_lan else None)
            }
        
        # 1. Process Tailscale Peers (Tier 2)
        for _, node in peers.items():
            hostname = node.get("HostName", "")
            if not hostname.startswith("gem-"): continue
                
            metadata = extract_metadata(hostname)
            if metadata["is_sidecar"]: continue # We only care about base session entries from TS status for now
            
            addrs = node.get("TailscaleIPs", [])
            ip = next((a for a in addrs if "." in a), None)
            
            if ip:
                machines_dict[hostname] = {
                    "name": hostname,
                    "project": metadata["project"],
                    "type": metadata["type"],
                    "uid": metadata["uid"],
                    "ip": ip,
                    "online": node.get("Online", False),
                    "local_url": local_ports.get(hostname),
                    "tiers": ["vpn"] if ip else []
                }
                if local_ports.get(hostname): machines_dict[hostname]["tiers"].insert(0, "local")

        # 2. Process Local Containers (Tier 1 & Sidecars)
        for hostname, local_url in local_ports.items():
            metadata = extract_metadata(hostname)
            parent = metadata["parent"]
            
            if metadata["is_sidecar"]:
                # 1. Ensure parent exists in dict
                if parent not in machines_dict:
                    machines_dict[parent] = {
                        "name": parent,
                        "project": metadata["project"],
                        "type": metadata["type"],
                        "uid": metadata["uid"],
                        "ip": None,
                        "online": True, # If we see its sidecar, we assume it's at least trying to be online
                        "local_url": None,
                        "tiers": []
                    }
                
                # 2. Enrich parent with sidecar info
                if metadata["sidecar_type"] not in machines_dict[parent]["tiers"]:
                    machines_dict[parent]["tiers"].append(metadata["sidecar_type"])
                continue

            if parent not in machines_dict:
                machines_dict[parent] = {
                    "name": parent,
                    "project": metadata["project"],
                    "type": metadata["type"],
                    "uid": metadata["uid"],
                    "ip": None,
                    "online": True,
                    "local_url": local_url,
                    "tiers": ["local"] if local_url else []
                }
            else:
                # Parent already exists from Tailscale, ensure local tier is marked
                if local_url and "local" not in machines_dict[parent]["tiers"]:
                    machines_dict[parent]["tiers"].insert(0, "local")
                    machines_dict[parent]["local_url"] = local_url
                
        machines = list(machines_dict.values())
        machines.sort(key=lambda x: x["name"])
        return machines
