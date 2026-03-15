from abc import ABC, abstractmethod
from typing import Dict
from app.models.session import GeminiSession

class DiscoveryProvider(ABC):
    """Base interface for all session discovery sources."""

    def is_available(self) -> bool:
        """Checks if the provider is available in the current environment."""
        return True
    
    @abstractmethod
    def get_sessions(self) -> Dict[str, GeminiSession]:
        """Returns a mapping of session_id -> GeminiSession."""
        pass
