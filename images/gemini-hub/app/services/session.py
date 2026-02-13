import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SessionService:
    """Manages the lifecycle of Gemini sessions."""

    @staticmethod
    def stop(session_id: str) -> Dict[str, Any]:
        """Stops a running session using docker stop."""
        
        # Security: Ensure session_id starts with 'gem-' to avoid stopping host containers
        if not session_id.startswith("gem-"):
            raise PermissionError(f"Invalid session ID: {session_id}. Only sessions starting with 'gem-' can be stopped.")

        cmd = ["docker", "stop", session_id]
        
        logger.info(f"Stopping session: {session_id}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "session_id": session_id
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr or f"Failed to stop session {session_id}",
                    "returncode": result.returncode
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"Error stopping session {session_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "returncode": -1
            }
