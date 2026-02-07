import subprocess
from unittest.mock import patch
from app.services.launcher import LauncherService

def test_launch_timeout():
    """Test handling of subprocess timeout."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gemini-toolbox", timeout=30)), \
         patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
        
        result = LauncherService.launch("/mock/root/project")
        
        assert result["returncode"] == -1
        assert "timed out" in result["stderr"]

def test_launch_exception():
    """Test handling of generic exception."""
    with patch("subprocess.run", side_effect=RuntimeError("Exec failed")), \
         patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
        
        result = LauncherService.launch("/mock/root/project")
        
        assert result["returncode"] == -1
        assert "Exec failed" in result["stderr"]

def test_launch_success_with_task():
    """Test successful launch with an autonomous task (interactive default)."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            result = LauncherService.launch("/mock/root/project", task="Hello Bot")
            
            assert result["returncode"] == 0
            args, _ = mock_run.call_args
            cmd = args[0]
            # Verify task is passed with -i by default
            assert cmd[-3:] == ["--", "-i", "Hello Bot"]

def test_launch_success_with_task_non_interactive():
    """Test successful launch with a non-interactive task."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            result = LauncherService.launch("/mock/root/project", task="Hello Bot", interactive=False)
            
            assert result["returncode"] == 0
            args, _ = mock_run.call_args
            cmd = args[0]
            # Verify task is passed without -i
            assert cmd[-2:] == ["--", "Hello Bot"]

def test_launch_with_variant_and_docker():
    """Test launch with preview variant and docker disabled."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            result = LauncherService.launch(
                "/mock/root/project", 
                image_variant='preview', 
                docker_enabled=False
            )
            
            assert result["returncode"] == 0
            args, _ = mock_run.call_args
            cmd = args[0]
            assert "--preview" in cmd
            assert "--no-docker" in cmd

def test_launch_with_worktree():
    """Test launch with worktree mode and explicit name."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            result = LauncherService.launch(
                "/mock/root/project", 
                worktree_mode=True,
                worktree_name="feat/new-ui"
            )
            
            assert result["returncode"] == 0
            args, _ = mock_run.call_args
            cmd = args[0]
            assert "--worktree" in cmd
            assert "--name" in cmd
            assert "feat/new-ui" in cmd

def test_launch_with_no_ide():
    """Test launch with IDE integration disabled."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            result = LauncherService.launch(
                "/mock/root/project", 
                ide_enabled=False
            )
            
            assert result["returncode"] == 0
            args, _ = mock_run.call_args
            cmd = args[0]
            assert "--no-ide" in cmd

