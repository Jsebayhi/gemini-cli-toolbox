import os
from typing import List

class Config:
    """Centralized configuration for the Gemini Hub."""
    
    # Discovery
    TAILSCALE_AUTH_KEY = os.environ.get("TAILSCALE_AUTH_KEY")
    
    # Roots (Normalized)
    _raw_roots = os.environ.get("HUB_ROOTS", "").split(":")
    _worktree_root = os.environ.get("GEMINI_WORKTREE_ROOT", "/cache/worktrees")
    
    HUB_ROOTS: List[str] = []
    
    # Process and normalize roots using os.path.normpath
    _seen = set()
    for r in _raw_roots + [_worktree_root]:
        r = r.strip()
        if r:
            r = os.path.normpath(r)
            if r not in _seen:
                HUB_ROOTS.append(r)
                _seen.add(r)

    # Lifecycle
    HUB_AUTO_SHUTDOWN = os.environ.get("HUB_AUTO_SHUTDOWN", "true").lower() == "true"
    HUB_WORKTREE_PRUNE_ENABLED = os.environ.get("HUB_WORKTREE_PRUNE_ENABLED", "true").lower() == "true"
    
    # Expiry settings (days)
    WORKTREE_EXPIRY_HEADLESS = int(os.environ.get("GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS", "30"))
    WORKTREE_EXPIRY_BRANCH = int(os.environ.get("GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS", "90"))
    WORKTREE_EXPIRY_ORPHAN = int(os.environ.get("GEMINI_WORKTREE_ORPHAN_EXPIRY_DAYS", "90"))

    # Compatibility aliases
    WORKTREE_ROOT = _worktree_root
    
    # Security & Paths
    HOST_CONFIG_ROOT = os.environ.get("HOST_CONFIG_ROOT", "/home/gemini/.gemini")
    HOST_HOME = os.environ.get("HOST_HOME", "/home/gemini")
    
    # Feature Flags
    HUB_NO_VPN = os.environ.get("GEMINI_HUB_NO_VPN", "false").lower() == "true"

    @staticmethod
    def validate():
        """Optional: Perform runtime validation of critical config."""
        pass
