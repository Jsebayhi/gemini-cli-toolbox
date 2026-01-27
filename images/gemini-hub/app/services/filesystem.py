import os
import logging
from typing import List, Dict, Optional
from app.config import Config

logger = logging.getLogger(__name__)

class FileSystemService:
    """Manages safe filesystem access for discovery."""

    @staticmethod
    def get_roots() -> List[str]:
        return Config.HUB_ROOTS

    @staticmethod
    def get_configs() -> List[str]:
        """Lists subdirectories in the HOST_CONFIG_ROOT."""
        root = Config.HOST_CONFIG_ROOT
        configs = []
        if os.path.isdir(root):
            try:
                configs = [d for d in os.listdir(root) 
                           if os.path.isdir(os.path.join(root, d))]
                configs.sort()
            except Exception as e:
                logger.error(f"Error listing configs in {root}: {e}")
        return configs

    @staticmethod
    def get_config_details(name: str) -> Dict[str, Any]:
        """Reads extra-args from a profile."""
        if not name:
            return {}
        
        profile_path = os.path.join(Config.HOST_CONFIG_ROOT, name)
        extra_args_path = os.path.join(profile_path, "extra-args")
        
        details = {"extra_args": []}
        if os.path.isfile(extra_args_path):
            try:
                with open(extra_args_path, 'r') as f:
                    args = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            args.append(line)
                    details["extra_args"] = args
            except Exception as e:
                logger.error(f"Error reading extra-args for {name}: {e}")
                
        return details

    @staticmethod
    def browse(path: str) -> Dict[str, Any]:
        """Lists subdirectories, restricted to HUB_ROOTS."""
        if not path:
            raise ValueError("Path required")
            
        # Security: Ensure path is within one of the HUB_ROOTS
        abs_path = os.path.abspath(path)
        allowed = any(abs_path.startswith(os.path.abspath(root)) for root in Config.HUB_ROOTS)
        
        if not allowed:
            raise PermissionError("Access denied")
            
        if not os.path.isdir(abs_path):
            raise FileNotFoundError("Not a directory")
            
        try:
            items = []
            for item in os.listdir(abs_path):
                full_path = os.path.join(abs_path, item)
                if os.path.isdir(full_path) and not item.startswith('.'):
                    items.append(item)
            items.sort()
            return {"path": abs_path, "directories": items}
        except Exception as e:
            logger.error(f"Error browsing {abs_path}: {e}")
            raise e
