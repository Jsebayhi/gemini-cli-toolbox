from unittest.mock import patch, MagicMock
from app.services.prune import PruneService
from app.config import Config

def test_prune_start_disabled():
    """Ensure prune doesn't start if disabled."""
    with patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", False), \
         patch("threading.Thread") as mock_thread:
        PruneService.start()
        mock_thread.assert_not_called()

def test_prune_start_enabled():
    """Ensure prune starts if enabled."""
    with patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", True), \
         patch("threading.Thread") as mock_thread:
        PruneService.start()
        mock_thread.assert_called_once()

def test_prune_skip_non_existent_root():
    """Ensure prune skips if root doesn't exist."""
    with patch.object(Config, "WORKTREE_ROOT", "/non-existent"), \
         patch("os.path.exists", return_value=False), \
         patch("os.listdir") as mock_ls:
        PruneService.prune()
        mock_ls.assert_not_called()

def test_prune_scan_error():
    """Test handling of os.listdir error during scan."""
    with patch.object(Config, "WORKTREE_ROOT", "/work"), \
         patch("os.path.exists", return_value=True), \
         patch("os.listdir", side_effect=Exception("Disk error")), \
         patch("logging.Logger.error") as mock_log:
        
        PruneService.prune()
        assert mock_log.called

def test_classify_and_prune_branch_stale():
    """Test pruning a stale branch worktree."""
    now = 1000 * 86400
    mtime = 900 * 86400 # 100 days old (stale for branch expiry 90)
    with patch("subprocess.run") as mock_run, \
         patch("os.path.getmtime", return_value=mtime), \
         patch("shutil.rmtree") as mock_rmtree, \
         patch.object(Config, "WORKTREE_EXPIRY_BRANCH", 90):
        
        mock_run.return_value.returncode = 0 # Branch
        res = PruneService.classify_and_prune("/mock/wt", now)
        assert res is True
        mock_rmtree.assert_called_once()

def test_classify_and_prune_headless_safe():
    """Test retention of a fresh headless worktree."""
    now = 1000 * 86400
    mtime = 990 * 86400 # 10 days old (safe for headless expiry 30)
    with patch("subprocess.run") as mock_run, \
         patch("os.path.getmtime", return_value=mtime), \
         patch("shutil.rmtree") as mock_rmtree, \
         patch.object(Config, "WORKTREE_EXPIRY_HEADLESS", 30):
        
        mock_run.return_value.returncode = 1 # Headless
        res = PruneService.classify_and_prune("/mock/wt", now)
        assert res is False
        mock_rmtree.assert_not_called()

def test_classify_and_prune_orphan_stale():
    """Test pruning a stale orphan worktree."""
    now = 1000 * 86400
    mtime = 900 * 86400 # 100 days old (stale for orphan expiry 90)
    with patch("subprocess.run") as mock_run, \
         patch("os.path.getmtime", return_value=mtime), \
         patch("shutil.rmtree") as mock_rmtree, \
         patch.object(Config, "WORKTREE_EXPIRY_ORPHAN", 90):
        
        mock_run.return_value.returncode = 128 # Error/Orphan
        res = PruneService.classify_and_prune("/mock/wt", now)
        assert res is True
        mock_rmtree.assert_called_once()

def test_classify_and_prune_git_exception():
    """Test handling of Git subprocess exception."""
    with patch("subprocess.run", side_effect=Exception("Git Error")), \
         patch("os.path.getmtime", return_value=0), \
         patch("shutil.rmtree") as mock_rmtree:
        
        res = PruneService.classify_and_prune("/mock/wt", 10**9)
        assert res is True # Expired orphan
        mock_rmtree.assert_called_once()

def test_prune_rmtree_failure():
    """Test handling of rmtree failure."""
    with patch("subprocess.run", return_value=MagicMock(returncode=0)), \
         patch("os.path.getmtime", return_value=0), \
         patch("shutil.rmtree", side_effect=OSError("Denied")):

        res = PruneService.classify_and_prune("/mock/wt", 10**9)
        assert res is False # Failed to remove

def test_prune_loop_exception_handling():
    """Test that the prune loop continues after an error."""
    with patch("app.services.prune.PruneService.prune", side_effect=[Exception("Scan failed"), Exception("Stop")]), \
         patch("time.sleep", side_effect=[None, Exception("Stop loop")]), \
         patch("logging.Logger.error") as mock_log:

        try:
            PruneService._prune_loop()
        except Exception:
            pass

        assert mock_log.called

