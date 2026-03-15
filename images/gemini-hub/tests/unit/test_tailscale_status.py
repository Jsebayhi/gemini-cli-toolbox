import subprocess
from unittest.mock import patch
from app.services.tailscale import TailscaleService

def test_get_status_success():
    """Test successful status retrieval."""
    mock_json = {"Peer": {}}

    with patch("os.path.exists", return_value=True), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"Peer": {}}'

        status = TailscaleService.get_status()
        assert status == mock_json

def test_get_status_no_socket():
    """Test handling of missing socket."""
    with patch("os.path.exists", return_value=False):
        status = TailscaleService.get_status()
        assert status == {}

def test_get_status_failure():
    """Test handling of tailscale command failure."""
    with patch("os.path.exists", return_value=True), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error"

        status = TailscaleService.get_status()
        assert status == {}

def test_get_status_timeout():
    """Test handling of subprocess timeout."""
    with patch("os.path.exists", return_value=True), \
         patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="tailscale", timeout=5)):
        status = TailscaleService.get_status()
        assert status == {}

def test_get_status_exception():
    """Test handling of generic exception."""
    with patch("os.path.exists", return_value=True), \
         patch("subprocess.run", side_effect=Exception("Boom")):
        status = TailscaleService.get_status()
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
