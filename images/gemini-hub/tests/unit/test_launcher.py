import pytest
import subprocess
from unittest.mock import patch, MagicMock
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
