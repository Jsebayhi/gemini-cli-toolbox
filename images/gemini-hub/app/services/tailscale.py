import json
import subprocess
import logging
import re
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
        """
        Unifies Tailscale peers and Docker containers into a single session list.
        Allows the Hub to discover local sessions even without VPN connectivity.
        """
        machines_dict = {}
        sidecars = set()
        
        # 1. Standalone Docker Scan (Tier 1)
        local_ports = TailscaleService.get_local_ports()
        
        # Regex for metadata parsing: gem-{project}-{type}-{uid}
        # Supports project names with hyphens
        metadata_regex = re.compile(r'^gem-(?P<project>.+)-(?P<type>[^-]+)-(?P<uid>[^-]+)$')

        # First pass: Identify primary local sessions
        for name, url in local_ports.items():
            if name.endswith("-vpn"):
                sidecars.add(name)
                continue
                
            match = metadata_regex.match(name)
            if match:
                machines_dict[name] = {
                    "name": name,
                    "project": match.group("project"),
                    "type": match.group("type"),
                    "uid": match.group("uid"),
                    "ip": None,
                    "online": True,
                    "local_url": url,
                    "tiers": ["local"],
                    "vpn_active": False
                }

        # 2. Merge with Tailscale Peers (Tier 2)
        peers = status_json.get("Peer", {})
        for _, node in peers.items():
            hostname = node.get("HostName", "")
            
            if not hostname.startswith("gem-"):
                continue
            
            if hostname.endswith("-vpn"):
                sidecars.add(hostname)
                continue

            addrs = node.get("TailscaleIPs", [])
            ip = next((a for a in addrs if "." in a), None)
            
            if not ip:
                continue

            if hostname in machines_dict:
                # Hybrid session: Update local session with VPN info
                machines_dict[hostname]["ip"] = ip
                machines_dict[hostname]["online"] = machines_dict[hostname]["online"] or node.get("Online", False)
                if "vpn" not in machines_dict[hostname]["tiers"]:
                    machines_dict[hostname]["tiers"].append("vpn")
            else:
                # Remote session or local session not currently exposing port 3000
                match = metadata_regex.match(hostname)
                if match:
                    machines_dict[hostname] = {
                        "name": hostname,
                        "project": match.group("project"),
                        "type": match.group("type"),
                        "uid": match.group("uid"),
                        "ip": ip,
                        "online": node.get("Online", False),
                        "local_url": None,
                        "tiers": ["vpn"],
                        "vpn_active": False
                    }

        # 3. Attribute sidecars to parents
        for sid in sidecars:
            parent = sid.replace("-vpn", "")
            if parent in machines_dict:
                machines_dict[parent]["vpn_active"] = True
                if "vpn" not in machines_dict[parent]["tiers"]:
                    machines_dict[parent]["tiers"].append("vpn")
                
        machines = list(machines_dict.values())
        machines.sort(key=lambda x: x["name"])
        return machines
