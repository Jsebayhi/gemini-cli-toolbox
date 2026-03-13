from unittest.mock import patch
from app.services.docker import DockerService

def test_get_local_ports_success():
    """Test parsing of docker ps output for local ports."""
    # Mock output: Name|Ports
    # gem-app-cli-123 | 0.0.0.0:32768->3000/tcp, :::32768->3000/tcp
    docker_output = """gem-my-app-cli-123|0.0.0.0:32768->3000/tcp
gem-other-app-bash-456|127.0.0.1:45000->3000/tcp
random-container|0.0.0.0:80->80/tcp"""

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = docker_output

        ports = DockerService.get_local_ports()
        assert len(ports) == 2
        assert ports["gem-my-app-cli-123"] == "http://localhost:32768"
        assert ports["gem-other-app-bash-456"] == "http://localhost:45000"

def test_get_local_ports_empty():
    """Test handling of no active containers."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""

        ports = DockerService.get_local_ports()
        assert ports == {}

def test_get_local_ports_failure():
    """Test handling of docker command failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Docker error"

        ports = DockerService.get_local_ports()
        assert ports == {}

def test_get_local_ports_exception():
    """Test handling of subprocess exception."""
    with patch("subprocess.run", side_effect=Exception("Boom")):
        ports = DockerService.get_local_ports()
        assert ports == {}
