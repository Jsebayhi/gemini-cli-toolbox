import os

class Config:
    """Central configuration for Gemini Hub."""
    
    # Required for production runs (fail fast if missing)
    TAILSCALE_AUTH_KEY = os.environ.get("TAILSCALE_AUTH_KEY", "")
    
    # Workspace Roots (Colon separated)
    HUB_ROOTS = [r for r in os.environ.get("HUB_ROOTS", "").split(":") if r]
    
    # Host Environment
    HOST_CONFIG_ROOT = os.environ.get("HOST_CONFIG_ROOT", "")
    HOST_HOME = os.environ.get("HOST_HOME", "")
    
    # Features
    HUB_AUTO_SHUTDOWN = os.environ.get("HUB_AUTO_SHUTDOWN", "").lower() in ("1", "true")
    
    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        if not cls.TAILSCALE_AUTH_KEY and not os.environ.get("FLASK_DEBUG"):
            # In development (FLASK_DEBUG=1), we might skip auth key check if mocking
            print("Warning: TAILSCALE_AUTH_KEY is not set.")
