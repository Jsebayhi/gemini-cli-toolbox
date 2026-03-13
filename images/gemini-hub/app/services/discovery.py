import logging
import re
from typing import List, Dict, Any
from app.services.docker import DockerService
from app.services.tailscale import TailscaleService

logger = logging.getLogger(__name__)

class DiscoveryService:
    """Orchestrates unified discovery of Gemini sessions."""

    @staticmethod
    def get_sessions() -> List[Dict[str, Any]]:
        """
        Unifies results from Docker and Tailscale into a single list.
        """
        machines_dict = {}
        
        # 1. Fetch Local Sessions from Docker (Standalone)
        local_ports = DockerService.get_local_ports()
        
        # Regex for metadata parsing: gem-{project}-{type}-{uid}
        metadata_regex = re.compile(r'^gem-(?P<project>.+)-(?P<type>[^-]+)-(?P<uid>[^-]+)$')

        for name, url in local_ports.items():
            match = metadata_regex.match(name)
            if match:
                machines_dict[name] = {
                    "name": name,
                    "project": match.group("project"),
                    "type": match.group("type"),
                    "uid": match.group("uid"),
                    "ip": None,
                    "online": True,
                    "local_url": url
                }

        # 2. Merge with Tailscale Peers
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

            if hostname in machines_dict:
                # Enrich existing local session with VPN info
                machines_dict[hostname]["ip"] = ip
                machines_dict[hostname]["online"] = machines_dict[hostname]["online"] or node.get("Online", False)
            else:
                # Add remote-only or port-hidden local session
                match = metadata_regex.match(hostname)
                if match:
                    machines_dict[hostname] = {
                        "name": hostname,
                        "project": match.group("project"),
                        "type": match.group("type"),
                        "uid": match.group("uid"),
                        "ip": ip,
                        "online": node.get("Online", False),
                        "local_url": None
                    }
                
        machines = list(machines_dict.values())
        machines.sort(key=lambda x: x["name"])
        return machines
