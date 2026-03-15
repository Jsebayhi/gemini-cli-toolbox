import re
from typing import Dict, Any, Optional

# Regex for metadata parsing: gem-{project}-{type}-{uid}
METADATA_REGEX = re.compile(r'^gem-(?P<project>.+)-(?P<type>[^-]+)-(?P<uid>[^-]+)$')

class GeminiSession:
    """Standardized representation of a Gemini session."""
    
    def __init__(self, name: str, project: str, session_type: str, uid: str):
        self.name = name
        self.project = project
        self.session_type = session_type
        self.uid = uid
        
        # State (Non-exclusive)
        self.is_running = False    # Local process exists
        self.is_reachable = False  # VPN link active (remote)
        
        # Details
        self.ip: Optional[str] = None
        self.local_url: Optional[str] = None

    @property
    def online(self) -> bool:
        """Unified status: session is active either locally or via VPN."""
        return self.is_running or self.is_reachable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "project": self.project,
            "type": self.session_type,
            "uid": self.uid,
            "is_running": self.is_running,
            "is_reachable": self.is_reachable,
            "online": self.is_running or self.is_reachable, # Legacy compat
            "ip": self.ip,
            "local_url": self.local_url
        }

    @staticmethod
    def from_name(name: str) -> Optional['GeminiSession']:
        """Parses a session name and returns a GeminiSession object."""
        match = METADATA_REGEX.match(name)
        if not match:
            return None
            
        return GeminiSession(
            name=name,
            project=match.group("project"),
            session_type=match.group("type"),
            uid=match.group("uid")
        )
