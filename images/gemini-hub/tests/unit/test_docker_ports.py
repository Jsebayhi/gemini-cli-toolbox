from unittest.mock import patch
from app.services.docker import DockerService

def test_docker_port_parsing_robustness():
    """
    Trophy: Unit Test (Precision).
    Verify that URL extraction works across various Docker output formats.
    """
    scenarios = [
        {
            "ports": "0.0.0.0:32768->3000/tcp", 
            "expected_url": "http://localhost:32768"
        },
        {
            "ports": "127.0.0.1:45000->3000/tcp, 0.0.0.0:80->80/tcp", 
            "expected_url": "http://localhost:45000"
        },
        {
            "ports": ":::32768->3000/tcp", # IPv6 bind
            "expected_url": "http://localhost:32768"
        },
        {
            "ports": "3000/tcp", # No mapping (internal only)
            "expected_url": None
        },
        {
            "ports": "", 
            "expected_url": None
        }
    ]
    
    for s in scenarios:
        docker_output = f"gem-test-cli-u1|{s['ports']}"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = docker_output
            
            sessions = DockerService().get_sessions()
            session = sessions["gem-test-cli-u1"]
            assert session.local_url == s["expected_url"], f"Failed scenario: {s}"

def test_docker_ps_empty_and_error():
    """Verify clean handling of empty or failing docker ps."""
    with patch("subprocess.run") as mock_run:
        # 1. Empty
        mock_run.return_value.stdout = ""
        assert DockerService().get_sessions() == {}
        
        # 2. Error
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Daemon Down"
        assert DockerService().get_sessions() == {}

def test_docker_service_availability():
    """Verify is_available logic across success and failures."""
    service = DockerService()
    
    with patch("subprocess.run") as mock_run:
        # 1. Success
        mock_run.return_value.returncode = 0
        assert service.is_available() is True
        
        # 2. Command Error
        mock_run.return_value.returncode = 1
        assert service.is_available() is False
        
        # 3. Exception (Subprocess error)
        mock_run.side_effect = Exception("OS Error")
        assert service.is_available() is False
        
        # 4. FileNotFoundError (Docker not installed)
        mock_run.side_effect = FileNotFoundError()
        assert service.is_available() is False

def test_docker_get_sessions_exception():
    """Verify exception safety in get_sessions."""
    with patch("subprocess.run", side_effect=Exception("Timeout")):
        assert DockerService().get_sessions() == {}


def test_docker_ps_invalid_json(mocker):
    """Trigger JSON parsing error in DockerService."""
    from app.services.docker import DockerService
    mocker.patch("subprocess.run", return_value=mocker.Mock(stdout="invalid json", returncode=0))
    service = DockerService()
    assert service.get_sessions() == {}

def test_docker_ps_generic_exception(mocker):
    """Trigger generic exception during Docker discovery."""
    from app.services.docker import DockerService
    mocker.patch("subprocess.run", side_effect=Exception("Subprocess failed"))
    service = DockerService()
    assert service.get_sessions() == {}
