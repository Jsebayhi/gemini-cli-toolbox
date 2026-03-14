import pytest
import subprocess
from app.services.launcher import LauncherService
from app.config import Config
from unittest.mock import patch

def test_build_launch_command_standard():
    """Test standard command construction."""
    with patch.object(Config, "HUB_NO_VPN", False):
        cmd, env = LauncherService.build_launch_command()
        assert "gemini-toolbox" in cmd
        assert "--remote" in cmd
        assert "--detached" in cmd

def test_build_launch_command_no_vpn():
    """Test command with --no-vpn when Hub is in local mode."""
    with patch.object(Config, "HUB_NO_VPN", True):
        cmd, env = LauncherService.build_launch_command()
        assert "--no-vpn" in cmd
        assert "--remote" not in cmd

def test_build_launch_command_preview_and_bash():
    """Test complex flag combination."""
    cmd, env = LauncherService.build_launch_command(
        session_type="bash",
        image_variant="preview"
    )
    assert "--bash" in cmd
    assert "--preview" in cmd

def test_build_launch_command_task_bot():
    """Test autonomous task (bot mode)."""
    cmd, env = LauncherService.build_launch_command(
        task="refactor",
        interactive=False
    )
    assert "--" in cmd
    assert "-p" in cmd
    assert "refactor" in cmd

def test_build_launch_command_custom_image():
    """Test using a custom image."""
    cmd, env = LauncherService.build_launch_command(
        custom_image="my-special-image"
    )
    assert "--image" in cmd
    assert "my-special-image" in cmd

def test_build_launch_command_disabled_features():
    """Test no-docker and no-ide flags."""
    cmd, env = LauncherService.build_launch_command(
        docker_enabled=False,
        ide_enabled=False
    )
    assert "--no-docker" in cmd
    assert "--no-ide" in cmd

def test_build_launch_command_worktree_named():
    """Test worktree with explicit name."""
    cmd, env = LauncherService.build_launch_command(
        worktree_mode=True,
        worktree_name="my-branch"
    )
    assert "--worktree" in cmd
    assert "--name" in cmd
    assert "my-branch" in cmd

def test_launcher_success():
    """Test successful launch integration."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run") as mock_run:
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"
        
        res = LauncherService.launch(project_path="/work")
        assert res["status"] == "success"
        assert res["stdout"] == "Success"

def test_launcher_permission_denied():
    """Test security check failure."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=False):
        with pytest.raises(PermissionError):
            LauncherService.launch(project_path="/forbidden")

def test_launcher_success_with_task():
    """Test successful launch with a task."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run") as mock_run:
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Task started"
        
        res = LauncherService.launch(project_path="/work", task="echo hello")
        assert res["status"] == "success"
        assert "--" in res["command"]
        assert "echo hello" in res["command"]

def test_launcher_command_failure():
    """Test handling of subprocess non-zero exit."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run") as mock_run:
        
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Already exists"
        
        res = LauncherService.launch(project_path="/work")
        assert res["status"] == "error"
        assert res["returncode"] == 1
        assert "Already exists" in res["stderr"]

def test_launcher_timeout():
    """Test subprocess timeout handling."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gemini", timeout=30)):
        
        res = LauncherService.launch(project_path="/work")
        assert res["status"] == "error"
        assert "timed out" in res["stderr"]

def test_launcher_exception():
    """Test generic exception handling."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run", side_effect=Exception("Crash")):
        
        res = LauncherService.launch(project_path="/work")
        assert res["status"] == "error"
        assert res["stderr"] == "Crash"
