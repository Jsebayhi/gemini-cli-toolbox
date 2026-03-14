from abc import ABC, abstractmethod
from typing import Dict
from app.models.session import GeminiSession

class DiscoveryProvider(ABC):
    """Base interface for all session discovery sources."""
    
    @abstractmethod
    def get_sessions(self) -> Dict[str, GeminiSession]:
        """Returns a mapping of session_id -> GeminiSession."""
        pass
