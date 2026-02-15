import pytest
from unittest.mock import patch, MagicMock
from app.services.session import SessionService

def test_stop_invalid_id():
    with pytest.raises(PermissionError):
        SessionService.stop("not-gem-id")

@patch("subprocess.run")
def test_stop_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="gem-session-id", stderr="")
    
    result = SessionService.stop("gem-session-id")
    
    assert result["status"] == "success"
    assert result["session_id"] == "gem-session-id"
    mock_run.assert_called_with(["docker", "stop", "gem-session-id"], capture_output=True, text=True, timeout=30)

@patch("subprocess.run")
def test_stop_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error message")
    
    result = SessionService.stop("gem-session-id")
    
    assert result["status"] == "error"
    assert "error message" in result["error"]

@patch("subprocess.run")
def test_stop_timeout(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd=["docker", "stop"], timeout=30)
    
    result = SessionService.stop("gem-session-id")
    
    assert result["status"] == "error"
    assert "timed out" in result["error"]

@patch("subprocess.run")
def test_stop_exception(mock_run):
    mock_run.side_effect = Exception("generic error")
    
    result = SessionService.stop("gem-session-id")
    
    assert result["status"] == "error"
    assert "generic error" in result["error"]
