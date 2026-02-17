import os
import shlex
import logging
from typing import List, Dict, Any
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
        """Reads extra-args from a profile, preserving all lines for UI display."""
        if not name:
            return {}
        
        profile_path = os.path.join(Config.HOST_CONFIG_ROOT, name)
        extra_args_path = os.path.join(profile_path, "extra-args")
        
        details = {"extra_args": []}
        if os.path.isfile(extra_args_path):
            try:
                with open(extra_args_path, 'r') as f:
                    lines_info = []
                    for line in f:
                        raw_line = line.rstrip('\n')
                        stripped = raw_line.strip()
                        
                        if not stripped:
                            lines_info.append({"type": "blank", "raw": raw_line})
                            continue
                            
                        if stripped.startswith('#'):
                            lines_info.append({"type": "comment", "raw": raw_line, "arg": "", "comment": stripped[1:].strip()})
                            continue
                            
                        try:
                            # Use shlex to identify the argument part
                            tokens = shlex.split(stripped, comments=True)
                            if not tokens:
                                lines_info.append({"type": "comment", "raw": raw_line, "arg": "", "comment": stripped.lstrip('#').strip()})
                                continue
                                
                            arg_part = " ".join(shlex.quote(t) for t in tokens)
                            
                            # Extract comment part
                            comment_part = ""
                            for i in range(len(stripped)):
                                if stripped[i] == '#':
                                    before = stripped[:i]
                                    try:
                                        if shlex.split(before) == tokens:
                                            comment_part = stripped[i+1:].strip()
                                            break
                                    except ValueError:
                                        continue
                            
                            lines_info.append({"type": "arg", "raw": raw_line, "arg": arg_part, "comment": comment_part})
                        except ValueError:
                            lines_info.append({"type": "arg", "raw": raw_line, "arg": stripped, "comment": ""})
                            
                    details["extra_args"] = lines_info
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
