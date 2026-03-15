import subprocess
from unittest.mock import patch
from app.services.tailscale import TailscaleService

def test_get_status_success():
    """Test successful status retrieval."""
    mock_json = {"Peer": {}}

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"Peer": {}}'
        
        service = TailscaleService()
        status = service.get_status()
        assert status == mock_json

def test_get_status_failure():
    """Test handling of tailscale command failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error"
        
        service = TailscaleService()
        status = service.get_status()
        assert status == {}

def test_get_status_timeout():
    """Test handling of subprocess timeout."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="tailscale", timeout=5)):
        service = TailscaleService()
        status = service.get_status()
        assert status == {}

def test_get_status_exception():
    """Test handling of generic exception."""
    with patch("subprocess.run", side_effect=Exception("Boom")):
        service = TailscaleService()
        status = service.get_status()
        assert status == {}

def test_get_status_invalid_json(mocker):
    """Trigger JSON parsing error in TailscaleService."""
    from app.services.tailscale import TailscaleService
    mocker.patch("subprocess.run", return_value=mocker.Mock(stdout="invalid json", returncode=0))
    service = TailscaleService()
    assert service.get_sessions() == {}

def test_get_status_generic_exception(mocker):
    """Trigger generic exception during Tailscale discovery."""
    from app.services.tailscale import TailscaleService
    mocker.patch("subprocess.run", side_effect=Exception("Status failed"))
    service = TailscaleService()
    assert service.get_sessions() == {}

def test_is_available_running(mocker):
    """Verify is_available returns True when sidecar is running."""
    from app.services.tailscale import TailscaleService
    mocker.patch("subprocess.run", return_value=mocker.Mock(stdout="true\n"))
    service = TailscaleService()
    assert service.is_available() is True

def test_is_available_not_running(mocker):
    """Verify is_available returns False when sidecar is not running."""
    from app.services.tailscale import TailscaleService
    mocker.patch("subprocess.run", return_value=mocker.Mock(stdout="false\n"))
    service = TailscaleService()
    assert service.is_available() is False

def test_is_available_exception(mocker):
    """Verify is_available handles exceptions gracefully."""
    from app.services.tailscale import TailscaleService
    mocker.patch("subprocess.run", side_effect=Exception("Docker failed"))
    service = TailscaleService()
    assert service.is_available() is False
