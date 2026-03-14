import logging
from typing import List, Dict, Any, Optional
from app.services.docker import DockerService
from app.services.tailscale import TailscaleService
from app.models.session import GeminiSession
from app.config import Config

logger = logging.getLogger(__name__)

class DiscoveryService:
    """Orchestrates unified discovery of Gemini sessions."""
    _instance = None

    def __new__(cls, providers=None):
        if not cls._instance:
            cls._instance = super(DiscoveryService, cls).__new__(cls)
            
            # Dynamic provider selection based on Pure Localhost mode
            if providers is not None:
                cls._instance.providers = providers
            else:
                cls._instance.providers = [DockerService()]
                if not Config.HUB_NO_VPN:
                    cls._instance.providers.append(TailscaleService())
                else:
                    logger.info("Pure Localhost mode active: Tailscale discovery disabled.")
                    
        return cls._instance

    @staticmethod
    def get_sessions() -> List[Dict[str, Any]]:
        """Static wrapper for convenience. Uses the singleton instance."""
        return DiscoveryService()._get_sessions_internal()

    @staticmethod
    def get_session_by_name(name: str) -> Optional[Dict[str, Any]]:
        """Finds a specific session by its name."""
        sessions = DiscoveryService.get_sessions()
        return next((s for s in sessions if s["name"] == name), None)

    def _get_sessions_internal(self) -> List[Dict[str, Any]]:
        """
        Unifies results from all registered providers into a single list of dicts.
        """
        master_map: Dict[str, GeminiSession] = {}
        
        for provider in self.providers:
            try:
                # 1. Skip if provider not available (e.g. docker daemon down)
                # We check for existence of method because of diverse mocks in legacy tests
                if hasattr(provider, "is_available") and not provider.is_available():
                    continue

                provider_sessions = provider.get_sessions()
                
                for name, session in provider_sessions.items():
                    if name not in master_map:
                        master_map[name] = session
                    else:
                        # 2. Strategic Merging (Priority & Aggregation)
                        existing = master_map[name]
                        
                        # Booleans are additive (OR)
                        if session.is_running:
                            existing.is_running = True
                        if session.is_reachable:
                            existing.is_reachable = True
                            
                        # Metadata Enrichment (Priority Logic)
                        # LOCAL info (Docker) always takes precedence over REMOTE info (Tailscale)
                        # We only overwrite if existing value is empty/None
                        if session.local_url and not existing.local_url:
                            existing.local_url = session.local_url
                        
                        if session.ip and not existing.ip:
                            existing.ip = session.ip
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
                
        # Convert to sorted list of dicts for API compatibility
        result = [s.to_dict() for s in master_map.values()]
        result.sort(key=lambda x: x["name"])
        return result
