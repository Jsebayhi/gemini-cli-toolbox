from unittest.mock import patch
from app.services.prune import PruneService
from app.config import Config

def test_prune_start_disabled():
    """Trophy: Basic Logic. Ensure prune doesn't start if disabled."""
    with patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", False), \
         patch("threading.Thread") as mock_thread:
        PruneService.start()
        mock_thread.assert_not_called()

def test_prune_start_enabled():
    """Trophy: Basic Logic. Ensure prune starts if enabled."""
    with patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", True), \
         patch("threading.Thread") as mock_thread:
        PruneService.start()
        mock_thread.assert_called_once()
