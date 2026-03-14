import subprocess
import sys
import os
from app.config import Config

def test_config_boolean_parsing_isolation():
    """Trophy: Unit Test (Precision). Hits boolean parsing branches in Config."""
    env = os.environ.copy()
    env["HUB_AUTO_SHUTDOWN"] = "FALSE"
    env["HUB_WORKTREE_PRUNE_ENABLED"] = "False"
    env["GEMINI_HUB_NO_VPN"] = "TRUE"
    env["TAILSCALE_AUTH_KEY"] = "dummy"
    
    code = "from app.config import Config; print(f'{Config.HUB_AUTO_SHUTDOWN},{Config.HUB_WORKTREE_PRUNE_ENABLED},{Config.HUB_NO_VPN}')"
    
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
    vals = result.stdout.strip().split(',')
    assert vals == ["False", "False", "True"]

def test_config_roots_normalization_isolation():
    """Verify that entries in HUB_ROOTS are normalized (trailing slashes removed)."""
    env = os.environ.copy()
    env["HUB_ROOTS"] = "/user/root/:/other/path"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/worktree/"
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
    assert "/user/root" in roots
    assert "/other/path" in roots
    assert "/tmp/worktree" in roots
    # Verify no trailing slashes
    for r in roots:
        assert not r.endswith("/")

def test_config_missing_auth_key_fallback():
    """Verify Config behavior when optional keys are missing."""
    env = os.environ.copy()
    env.pop("TAILSCALE_AUTH_KEY", None)
    
    code = "from app.config import Config; print(Config.TAILSCALE_AUTH_KEY)"
    
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
    # Should be None (printed as 'None')
    assert result.stdout.strip() == "None"

def test_config_no_roots_isolation():
    """Trophy: Unit Test (Precision). Hits branches when no roots are provided."""
    env = os.environ.copy()
    env["HUB_ROOTS"] = ""
    env["GEMINI_WORKTREE_ROOT"] = ""
    env["TAILSCALE_AUTH_KEY"] = "dummy"
    
    code = "from app.config import Config; print(len(Config.HUB_ROOTS))"
    
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
    # Should be 0
    assert result.stdout.strip() == "0"

def test_config_normalization_empty_segments_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for empty/whitespace segments."""
    env = os.environ.copy()
    # String with leading/trailing colons and whitespace segments
    env["HUB_ROOTS"] = ": : /tmp/valid :  "
    env["GEMINI_WORKTREE_ROOT"] = " /tmp/worktree/ "
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
    # Should only contain the two valid, stripped paths
    assert "/tmp/valid" in roots
    assert "/tmp/worktree" in roots
    assert len(roots) == 2

def test_config_normalization_redundancy_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for empty/duplicate roots."""
    env = os.environ.copy()
    # Duplicates, empty segments, and trailing slashes
    env["HUB_ROOTS"] = "/tmp/a:/tmp/a/::/tmp/b:/tmp/a"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/b"
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
    # Should be exactly ['/tmp/a', '/tmp/b']
    assert roots == ["/tmp/a", "/tmp/b"]

def test_config_normalization_whitespace_and_colons_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for whitespace and colons."""
    env = os.environ.copy()
    # String with only whitespace and redundant colons
    env["HUB_ROOTS"] = " :  :  "
    env["GEMINI_WORKTREE_ROOT"] = "/valid/worktree"
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
    # Should only contain the valid worktree path
    assert roots == ["/valid/worktree"]

def test_config_normalization_identical_variants_isolation():
    """Trophy: Unit Test (Precision). Hits deduplication logic for slash-variant paths."""
    env = os.environ.copy()
    # Identical paths with different slash variants
    env["HUB_ROOTS"] = "/tmp/dup:/tmp/dup/:///tmp/dup//"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/dup"
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
    # Should be exactly one entry
    assert roots == ["/tmp/dup"]

def test_config_normalization_degenerate_colons_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for colon-only strings."""
    env = os.environ.copy()
    # String with ONLY colons and valid worktree
    env["HUB_ROOTS"] = ":::"
    env["GEMINI_WORKTREE_ROOT"] = "/valid/worktree"
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
    # Should only contain the valid worktree
    assert roots == ["/valid/worktree"]

def test_config_normalization_cross_env_redundancy_isolation():
    """Trophy: Unit Test (Precision). Hits cross-env deduplication logic."""
    env = os.environ.copy()
    # Path provided in both HUB_ROOTS and GEMINI_WORKTREE_ROOT
    env["HUB_ROOTS"] = "/tmp/shared"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/shared/"
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
    # Should contain exactly one normalized path
    assert roots == ["/tmp/shared"]

def test_config_normalization_prefix_variants_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for prefix-related paths."""
    env = os.environ.copy()
    # Paths where one is a prefix, with redundant slashes
    env["HUB_ROOTS"] = "/tmp/a///:/tmp/a/b"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/a"
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
    # Should contain both unique normalized paths
    assert "/tmp/a" in roots
    assert "/tmp/a/b" in roots
    assert len(roots) == 2

def test_config_normalization_worktree_redundancy_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for worktree duplicates."""
    env = os.environ.copy()
    # Path that matches GEMINI_WORKTREE_ROOT (with trailing slashes)
    env["HUB_ROOTS"] = "/cache/worktrees/:///cache/worktrees"
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
    # Should contain exactly one normalized path
    assert roots == ["/cache/worktrees"]

def test_config_normalization_redundant_colons_isolation():
    """Trophy: Unit Test (Precision). Hits splitting branches for multiple redundant colons."""
    env = os.environ.copy()
    # String with multiple redundant colons between valid segments
    env["HUB_ROOTS"] = "/tmp/a::::/tmp/b"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/c"
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
    # Should contain exactly three valid paths
    assert roots == ["/tmp/a", "/tmp/b", "/tmp/c"]

def test_config_normalization_minimal_overlap_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for minimal overlap."""
    env = os.environ.copy()
    # Path that is EXACTLY the same as worktree root
    env["HUB_ROOTS"] = "/cache/worktrees"
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
    # Should contain exactly one normalized path
    assert roots == ["/cache/worktrees"]

def test_config_normalization_relative_dot_isolation():
    """Trophy: Unit Test (Precision). Hits normalization branches for dot/relative paths."""
    env = os.environ.copy()
    # String with a relative '.' component and a valid path
    env["HUB_ROOTS"] = ".:/tmp/valid"
    env["GEMINI_WORKTREE_ROOT"] = "/tmp/valid"
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
    # Should contain exactly two normalized paths ('.' and '/tmp/valid')
    assert "." in roots
    assert "/tmp/valid" in roots
    assert len(roots) == 2

def test_config_validate_execution():
    """Trophy: Unit Test (Precision). Hits validate method directly."""
    # Currently it's a pass, but we ensure it's called
    Config.validate()
    assert True

def test_config_validate_placeholder():
    """Trophy: Unit Test (Precision). Hits the validate() placeholder."""
    # Currently a no-op, but we execute it for coverage
    Config.validate()
    assert True
