import subprocess
import sys
import os

def test_config_initialization_isolation():
    """Verify Config initialization in an isolated process to test environment variable parsing."""
    env = os.environ.copy()
    env["HUB_ROOTS"] = "/projects:/data"
    env["GEMINI_WORKTREE_ROOT"] = "/cache/worktrees"
    env["TAILSCALE_AUTH_KEY"] = "dummy"
    
    # We use a small python script to check the initialized Config
    code = "from app.config import Config; print(','.join(Config.HUB_ROOTS))"
    
    # Ensure the current directory is in PYTHONPATH
    current_env = os.environ.copy()
    current_env.update(env)
    
    result = subprocess.run(
        [sys.executable, "-c", code], 
        env=current_env, 
        capture_output=True, 
        text=True,
        cwd="/app" # Integration tests run in /app in the container
    )
    
    assert result.returncode == 0
    roots = result.stdout.strip().split(',')
    assert "/projects" in roots
    assert "/data" in roots
    assert "/cache/worktrees" in roots
    assert len(roots) == 3

def test_config_no_duplicates_isolation():
    """Verify that duplicates are avoided during initialization."""
    env = os.environ.copy()
    env["HUB_ROOTS"] = "/projects:/cache/worktrees"
    env["GEMINI_WORKTREE_ROOT"] = "/cache/worktrees"
    env["TAILSCALE_AUTH_KEY"] = "dummy"
    
    code = "from app.config import Config; print(','.join(Config.HUB_ROOTS))"
    
    current_env = os.environ.copy()
    current_env.update(env)
    
    result = subprocess.run(
        [sys.executable, "-c", code], 
        env=current_env, 
        capture_output=True, 
        text=True,
        cwd="/app"
    )
    
    assert result.returncode == 0
    roots = result.stdout.strip().split(',')
    assert "/projects" in roots
    assert roots.count("/cache/worktrees") == 1
    assert len(roots) == 2
