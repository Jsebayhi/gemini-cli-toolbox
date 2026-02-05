import os
import time
import shutil
from app.services.prune import PruneService
from app.config import Config

def test_prune_prune(tmp_path, mocker):
    # Setup mock worktree structure
    worktree_root = tmp_path / "worktrees"
    worktree_root.mkdir()
    
    project_dir = worktree_root / "test-project"
    project_dir.mkdir()
    
    # 1. Fresh worktree (should stay)
    fresh_path = project_dir / "fresh"
    fresh_path.mkdir()
    
    # 2. Stale branch worktree (90d default, set to 100d -> delete)
    stale_branch_path = project_dir / "stale-branch"
    stale_branch_path.mkdir()
    
    # 3. Fresh headless worktree (should stay)
    fresh_headless_path = project_dir / "exploration-fresh"
    fresh_headless_path.mkdir()
    
    # 4. Stale headless worktree (30d default, set to 40d -> delete)
    stale_headless_path = project_dir / "exploration-stale"
    stale_headless_path.mkdir()
    
    # Mock config
    Config.WORKTREE_ROOT = str(worktree_root)
    Config.WORKTREE_EXPIRY_HEADLESS = 30
    Config.WORKTREE_EXPIRY_BRANCH = 90
    Config.WORKTREE_EXPIRY_ORPHAN = 90
    
    # Mock Git responses
    def mock_git_run(cmd, **kwargs):
        path = cmd[2]
        class MockResult:
            def __init__(self, code): self.returncode = code
        
        if "stale-branch" in path or "fresh" in path:
            return MockResult(0) # Branch
        if "exploration" in path:
            return MockResult(1) # Headless
        return MockResult(128) # Error
        
    mocker.patch("subprocess.run", side_effect=mock_git_run)
    
    now = time.time()
    
    # Set branch stale (100 days)
    mtime_branch = now - (100 * 86400)
    os.utime(stale_branch_path, (mtime_branch, mtime_branch))
    
    # Set headless stale (40 days)
    mtime_headless = now - (40 * 86400)
    os.utime(stale_headless_path, (mtime_headless, mtime_headless))
    
    # Run prune
    PruneService.prune()
    
    # Verify
    assert fresh_path.exists()
    assert fresh_headless_path.exists()
    assert not stale_branch_path.exists()
    assert not stale_headless_path.exists()



def test_prune_skip_non_dir(tmp_path):
    worktree_root = tmp_path / "worktrees"
    worktree_root.mkdir()
    
    dummy_file = worktree_root / "not-a-dir.txt"
    dummy_file.write_text("hello")
    
    Config.WORKTREE_ROOT = str(worktree_root)
    
    # Should not crash
    PruneService.prune()
    assert dummy_file.exists()

def test_prune_disabled(mocker):
    # Setup
    Config.HUB_WORKTREE_PRUNE_ENABLED = False
    mock_thread = mocker.patch("threading.Thread")
    
    # Run
    PruneService.start()
    
    # Verify
    mock_thread.assert_not_called()


