import os
import subprocess
import logging
from typing import Dict
from app.config import Config

logger = logging.getLogger(__name__)

class LauncherService:
    """Manages the execution of gemini-toolbox sessions."""

    @staticmethod
    def launch(project_path: str, config_profile: str = None, session_type: str = 'cli', task: str = None, interactive: bool = True, image_variant: str = 'standard', docker_enabled: bool = True, worktree_mode: bool = False, worktree_name: str = None, ide_enabled: bool = True) -> Dict[str, str]:
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

        if image_variant == 'preview':
            config_args.append("--preview")

        if not docker_enabled:
            config_args.append("--no-docker")

        if not ide_enabled:
            config_args.append("--no-ide")

        if worktree_mode:
            config_args.append("--worktree")
            if worktree_name:
                config_args.extend(["--name", worktree_name])

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
            # Autonomous mode logic
            if interactive:
                 cmd.extend(["--", "-i", task])
            else:
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
