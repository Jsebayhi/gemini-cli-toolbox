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
    """Test successful launch with an autonomous task."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            result = LauncherService.launch("/mock/root/project", task="Hello Bot")
            
            assert result["returncode"] == 0
            args, _ = mock_run.call_args
            cmd = args[0]
            # Verify task is passed after --
            assert cmd[-2:] == ["--", "Hello Bot"]

