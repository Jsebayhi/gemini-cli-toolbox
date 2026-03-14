import subprocess
import logging
from typing import Dict
from app.models.session import GeminiSession
from app.services.base import DiscoveryProvider

logger = logging.getLogger(__name__)

class DockerService(DiscoveryProvider):
    """Session Provider for local Docker containers."""

    def is_available(self) -> bool:
        """Checks if the Docker daemon is reachable."""
        try:
            # Lightweight check: docker info or version
            cmd = ["docker", "ps", "-q"]
            res = subprocess.run(cmd, capture_output=True, timeout=2)
            return res.returncode == 0
        except Exception:
            return False

    def get_sessions(self) -> Dict[str, GeminiSession]:
        """
        Returns GeminiSession objects for all running 
        Gemini containers on the local daemon.
        """
        sessions = {}
        try:
            # We use "docker ps" to find containers with the gem- prefix.
            cmd = ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode != 0:
                logger.error(f"Docker ps error: {result.stderr}")
                return {}

            for line in result.stdout.strip().split('\n'):
                if not line or "|" not in line:
                    continue
                
                name, ports_str = line.split('|', 1)
                if not name.startswith("gem-"):
                    continue
                
                session = GeminiSession.from_name(name)
                if not session:
                    continue
                    
                # A container in 'docker ps' is running locally
                session.is_running = True
                
                # Identify port 3000 mapping
                for part in ports_str.split(','):
                    part = part.strip()
                    if "->3000/tcp" in part:
                        left = part.split("->")[0]
                        if ":" in left:
                            host_port = left.split(":")[-1]
                            session.local_url = f"http://localhost:{host_port}"
                            break
                
                sessions[name] = session
                    
            return sessions
        except Exception as e:
            logger.error(f"Error getting docker sessions: {e}")
            return {}
