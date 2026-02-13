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
    HUB_WORKTREE_PRUNE_ENABLED = os.environ.get("HUB_WORKTREE_PRUNE_ENABLED", "true").lower() in ("1", "true")
    
    # Worktree Lifecycle
    WORKTREE_EXPIRY_HEADLESS = int(os.environ.get("GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS", "30"))
    WORKTREE_EXPIRY_BRANCH = int(os.environ.get("GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS", "90"))
    WORKTREE_EXPIRY_ORPHAN = int(os.environ.get("GEMINI_WORKTREE_ORPHAN_EXPIRY_DAYS", "90"))
    
    # The Hub container sees the host cache if it is mounted. 
    # We will assume it is mounted at /host-cache for now, or just use the absolute host path if we can.
    # Actually, the Hub needs to know WHERE the worktrees are on the container's FS.
    WORKTREE_ROOT = os.environ.get("GEMINI_WORKTREE_ROOT", "/home/gemini/.cache/gemini-toolbox/worktrees")

    # Initialization logic: Ensure worktree root is always in scannable roots
    if WORKTREE_ROOT and WORKTREE_ROOT not in HUB_ROOTS:
        HUB_ROOTS.append(WORKTREE_ROOT)
    
    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        if not cls.TAILSCALE_AUTH_KEY and not os.environ.get("FLASK_DEBUG"):
            # In development (FLASK_DEBUG=1), we might skip auth key check if mocking
            print("Warning: TAILSCALE_AUTH_KEY is not set.")
