import os
import subprocess
import logging
from typing import Dict, List, Tuple, Any
from app.config import Config
from app.services.filesystem import FileSystemService

logger = logging.getLogger(__name__)

class LauncherService:
    """Manages the execution of gemini-toolbox sessions."""

    @staticmethod
    def launch(project_path: str, config_profile: str = None, session_type: str = 'cli', task: str = None, interactive: bool = True, image_variant: str = 'standard', docker_enabled: bool = True, worktree_mode: bool = False, worktree_name: str = None, ide_enabled: bool = True, custom_image: str = None, docker_args: str = None) -> Dict[str, Any]:
        """Launches gemini-toolbox via subprocess."""
        
        # Security Check
        abs_path = os.path.abspath(project_path)
        if not FileSystemService.is_safe_path(abs_path):
            raise PermissionError(f"Access denied to {project_path}")

        # Build Args and Environment
        cmd, env = LauncherService.build_launch_command(
            config_profile, session_type, task, interactive, 
            image_variant, docker_enabled, worktree_mode, 
            worktree_name, ide_enabled, custom_image, docker_args
        )

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
                "returncode": result.returncode,
                "status": "success" if result.returncode == 0 else "error"
            }
        except subprocess.TimeoutExpired:
            return {
                "command": cmd_str,
                "stdout": "",
                "stderr": "Error: Command timed out",
                "returncode": -1,
                "status": "error"
            }
        except Exception as e:
            return {
                "command": cmd_str,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "status": "error"
            }

    @staticmethod
    def build_launch_command(config_profile: str = None, session_type: str = 'cli', 
                            task: str = None, interactive: bool = True, 
                            image_variant: str = 'standard', docker_enabled: bool = True, 
                            worktree_mode: bool = False, worktree_name: str = None, 
                            ide_enabled: bool = True, custom_image: str = None, 
                            docker_args: str = None) -> Tuple[List[str], Dict[str, str]]:
        """Constructs the command array and environment variables."""
        
        config_args = []
        if config_profile:
            profile_path = os.path.join(Config.HOST_CONFIG_ROOT, config_profile)
            config_args = ["--profile", profile_path]

        if session_type == 'bash':
            config_args.append("--bash")

        if custom_image:
            config_args.extend(["--image", custom_image])
        elif image_variant == 'preview':
            config_args.append("--preview")

        if not docker_enabled:
            config_args.append("--no-docker")

        if not ide_enabled:
            config_args.append("--no-ide")

        if docker_args:
            config_args.extend(["--docker-args", docker_args])

        if worktree_mode:
            config_args.append("--worktree")
            if worktree_name:
                config_args.extend(["--name", worktree_name])

        # Base command: always --remote and --detached from Hub
        # But if HUB_NO_VPN is enabled, we use --no-vpn instead of --remote
        cmd = ["gemini-toolbox", "--detached"]
        if Config.HUB_NO_VPN:
            cmd.append("--no-vpn")
        else:
            cmd.append("--remote")
            
        cmd += config_args
        
        if task:
            # Autonomous mode logic
            if interactive:
                 cmd.extend(["--", "-i", task])
            else:
                 cmd.extend(["--", "-p", task])

        # Prepare Environment
        env = os.environ.copy()
        if Config.HOST_HOME:
            env["HOME"] = Config.HOST_HOME
        
        # Pass Key via Env (Security Best Practice)
        env["GEMINI_REMOTE_KEY"] = Config.TAILSCALE_AUTH_KEY
        
        return cmd, env
