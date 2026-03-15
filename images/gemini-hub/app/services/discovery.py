import logging
from typing import List, Dict, Any
from app.services.docker import DockerService
from app.services.tailscale import TailscaleService

logger = logging.getLogger(__name__)

class DiscoveryService:
    """Orchestrates unified discovery of Gemini sessions."""

    def __init__(self, providers=None):
        """
        Initializes the service with discovery providers.
        Defaults to Docker and Tailscale if none provided.
        """
        if providers is not None:
            self.providers = providers
        else:
            self.providers = [
                DockerService(),
                TailscaleService()
            ]

    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Unifies results from all registered providers into a single list of dicts.
        """
        master_map: Dict[str, Dict[str, Any]] = {}
        
        for provider in self.providers:
            try:
                # 1. Skip if provider not available (e.g. docker daemon down)
                if not provider.is_available():
                    continue

                provider_sessions = provider.get_sessions()
                
                for name, session in provider_sessions.items():
                    if name not in master_map:
                        master_map[name] = session.to_dict()
                    else:
                        # 2. Strategic Merging (Priority & Aggregation)
                        existing = master_map[name]
                        
                        # Booleans are additive (OR)
                        if session.is_running:
                            existing["is_running"] = True
                        if session.is_reachable:
                            existing["is_reachable"] = True
                        
                        # Recalculate online status
                        existing["online"] = existing["is_running"] or existing["is_reachable"]
                            
                        # Metadata Enrichment (Priority Logic)
                        if session.local_url and not existing.get("local_url"):
                            existing["local_url"] = session.local_url
                        
                        if session.ip and not existing.get("ip"):
                            existing["ip"] = session.ip
            except (Exception, AttributeError, TypeError) as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
                
        # Convert to sorted list of dicts for API compatibility
        result = list(master_map.values())
        result.sort(key=lambda x: x["name"])
        return result
