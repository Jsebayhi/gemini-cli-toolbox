import subprocess
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class DockerService:
    """Manages interactions with the local Docker daemon."""

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
                logger.error(f"Docker ps error: {result.stderr}")
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
