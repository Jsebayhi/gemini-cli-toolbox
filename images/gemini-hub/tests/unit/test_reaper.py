import os
import time
import shutil
from app.services.reaper import ReaperService
from app.config import Config

def test_reaper_prune(tmp_path):
    # Setup mock worktree structure
    worktree_root = tmp_path / "worktrees"
    worktree_root.mkdir()
    
    project_dir = worktree_root / "test-project"
    project_dir.mkdir()
    
    # 1. Fresh worktree (should stay)
    fresh_path = project_dir / "fresh"
    fresh_path.mkdir()
    
    # 2. Stale worktree (should be deleted)
    stale_path = project_dir / "stale"
    stale_path.mkdir()
    
    # Mock config
    Config.WORKTREE_ROOT = str(worktree_root)
    Config.WORKTREE_EXPIRY_DAYS = 1 # 1 day for test
    
    # Manipulate mtime of the stale path
    # Set it to 2 days ago
    stale_mtime = time.time() - (2 * 86400)
    os.utime(stale_path, (stale_mtime, stale_mtime))
    
    # Run prune
    ReaperService.prune()
    
    # Verify
    assert fresh_path.exists()
    assert not stale_path.exists()
    assert project_dir.exists()

def test_reaper_skip_non_dir(tmp_path):
    worktree_root = tmp_path / "worktrees"
    worktree_root.mkdir()
    
    dummy_file = worktree_root / "not-a-dir.txt"
    dummy_file.write_text("hello")
    
    Config.WORKTREE_ROOT = str(worktree_root)
    
    # Should not crash
    ReaperService.prune()
    assert dummy_file.exists()
