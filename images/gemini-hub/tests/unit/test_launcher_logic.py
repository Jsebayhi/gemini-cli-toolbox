import pytest
from unittest.mock import patch
import subprocess
from app.services.launcher import LauncherService
from app.config import Config

def test_launcher_success_standard():
    """Test standard launch with VPN enabled (Default)."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run") as mock_run, \
         patch.object(Config, "HUB_NO_VPN", False):
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"
        
        res = LauncherService.launch(project_path="/work")
        assert "--remote" in res["command"]
        assert "--no-vpn" not in res["command"]

def test_launcher_permission_denied():
    """Test security check failure."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=False):
        with pytest.raises(PermissionError):
            LauncherService.launch(project_path="/forbidden")

def test_launcher_command_failure():
    """Test handling of subprocess non-zero exit."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run") as mock_run:
        
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Already exists"
        
        res = LauncherService.launch(project_path="/work")
        assert res["returncode"] == 1
        assert "Already exists" in res["stderr"]

def test_launcher_timeout():
    """Test subprocess timeout handling."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gemini", timeout=30)):
        
        res = LauncherService.launch(project_path="/work")
        assert "timed out" in res["stderr"]
