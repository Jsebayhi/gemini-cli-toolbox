import json
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TailscaleService:
    """Manages interactions strictly with the Tailscale daemon."""

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
