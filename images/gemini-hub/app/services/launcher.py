import os
import subprocess
import logging
from typing import Dict
from app.config import Config

logger = logging.getLogger(__name__)

class LauncherService:
    """Manages the execution of gemini-toolbox sessions."""

    @staticmethod
    def launch(project_path: str, config_profile: str = None, session_type: str = 'cli', task: str = None) -> Dict[str, str]:
        """Launches gemini-toolbox via subprocess."""
        
        # Security Check
        abs_path = os.path.abspath(project_path)
        allowed = any(abs_path.startswith(os.path.abspath(root)) for root in Config.HUB_ROOTS)
        if not allowed:
            raise PermissionError(f"Access denied to {project_path}")

        # Build Args
        config_args = []
        if config_profile:
            profile_path = os.path.join(Config.HOST_CONFIG_ROOT, config_profile)
            config_args = ["--profile", profile_path]

        if session_type == 'bash':
            config_args.append("--bash")

        # Prepare Environment
        env = os.environ.copy()
        if Config.HOST_HOME:
            env["HOME"] = Config.HOST_HOME
        
        # Pass Key via Env (Security Best Practice)
        env["GEMINI_REMOTE_KEY"] = Config.TAILSCALE_AUTH_KEY
            
        # Command Construction
        # We pass --remote without the key value since it's in env
        cmd = ["gemini-toolbox", "--remote", "--detached"] + config_args
        
        if task:
            # Autonomous mode: pass the task as arguments to gemini
            cmd.extend(["--", task])

        cmd_str = ' '.join(cmd)
        
        logger.info(f"Executing: {cmd_str} in {project_path}")
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=project_path, 
                env=env, 
                capture_output=True, 
                text=True,
                timeout=30 # Safety timeout for startup
            )
            
            return {
                "command": cmd_str,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "command": cmd_str,
                "stdout": "",
                "stderr": "Error: Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "command": cmd_str,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
