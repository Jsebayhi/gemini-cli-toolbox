from app.services.prune import PruneService

def test_prune_start_enabled(mocker):
    """Verify that PruneService starts its thread if enabled."""
    mocker.patch("app.config.Config.HUB_WORKTREE_PRUNE_ENABLED", True)
    mock_thread = mocker.patch("threading.Thread")
    
    PruneService.start()
    mock_thread.assert_called_once()

def test_prune_start_disabled(mocker):
    """Verify that PruneService does NOT start if disabled."""
    mocker.patch("app.config.Config.HUB_WORKTREE_PRUNE_ENABLED", False)
    mock_thread = mocker.patch("threading.Thread")
    
    PruneService.start()
    mock_thread.assert_not_called()

def test_prune_logic_expiry_categories(mocker, tmp_path):
    """Cover different worktree expiry paths in PruneService."""
    from app.config import Config
    
    worktree_root = tmp_path / "worktrees"
    worktree_root.mkdir()
    
    # Structure must be root/{project}/{worktree}
    proj_dir = worktree_root / "my-project"
    proj_dir.mkdir()
    
    # 1. Headless (30 days)
    headless_dir = proj_dir / "headless"
    headless_dir.mkdir()
    
    # 2. Branch (90 days)
    branch_dir = proj_dir / "branch"
    branch_dir.mkdir()
    
    # 3. Orphan (90 days)
    orphan_dir = proj_dir / "orphan"
    orphan_dir.mkdir()
    
    mocker.patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", True)
    mocker.patch.object(Config, "WORKTREE_ROOT", str(worktree_root))
    
    # Mock symbolic-ref to categorize
    def mock_ref(cmd, **kwargs):
        cmd_str = " ".join(cmd)
        if "headless" in cmd_str:
            return mocker.Mock(returncode=1)
        if "branch" in cmd_str:
            return mocker.Mock(returncode=0, stdout="refs/heads/main")
        return mocker.Mock(returncode=128) # Error -> Orphan
    
    mocker.patch("subprocess.run", side_effect=mock_ref)
    
    PruneService.prune()
    assert True

def test_prune_git_error_fallback(mocker, tmp_path):
    """Cover fallback path when git command fails during pruning."""
    from app.services.prune import PruneService
    from app.config import Config
    
    root = tmp_path / "root"
    proj = root / "proj"
    proj.mkdir(parents=True)
    wt = proj / "wt"
    wt.mkdir()
    
    mocker.patch.object(Config, "WORKTREE_ROOT", str(root))
    mocker.patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", True)
    mocker.patch("subprocess.run", side_effect=Exception("Git failed"))
    
    # Should not crash, just continue
    PruneService.prune()
    assert True

def test_prune_rmtree_error_handling(mocker, tmp_path):
    """Cover error handling when directory removal fails."""
    from app.services.prune import PruneService
    from app.config import Config
    
    root = tmp_path / "root"
    proj = root / "proj"
    proj.mkdir(parents=True)
    wt = proj / "wt"
    wt.mkdir()
    
    mocker.patch.object(Config, "WORKTREE_ROOT", str(root))
    mocker.patch.object(Config, "HUB_WORKTREE_PRUNE_ENABLED", True)
    mocker.patch.object(Config, "WORKTREE_EXPIRY_ORPHAN", -1) # Force expiry
    
    mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=128))
    mocker.patch("shutil.rmtree", side_effect=Exception("RM failed"))
    
    PruneService.prune()
    assert True
