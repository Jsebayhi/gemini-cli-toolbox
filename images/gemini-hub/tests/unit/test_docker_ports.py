from unittest.mock import patch
from app.services.docker import DockerService

def test_get_sessions_success():
    """Test parsing of docker ps output for Gemini sessions."""
    # Mock output: Name|Ports
    docker_output = """gem-my-app-cli-123|0.0.0.0:32768->3000/tcp
gem-other-app-bash-456|127.0.0.1:45000->3000/tcp"""

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = docker_output

        sessions = DockerService().get_sessions()
        assert len(sessions) == 2
        
        s1 = sessions["gem-my-app-cli-123"]
        assert s1.project == "my-app"
        assert s1.is_running is True
        assert s1.local_url == "http://localhost:32768"

def test_get_sessions_malformed():
    """Test handling of malformed lines in docker ps."""
    docker_output = "malformed-line-without-pipe\ngem-valid-cli-1|127.0.0.1:3000->3000/tcp"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = docker_output
        sessions = DockerService().get_sessions()
        assert len(sessions) == 1

def test_get_sessions_command_failure():
    """Test handling of docker command failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error"
        sessions = DockerService().get_sessions()
        assert sessions == {}

def test_get_sessions_exception():
    """Test handling of subprocess exception."""
    with patch("subprocess.run", side_effect=Exception("Boom")):
        sessions = DockerService().get_sessions()
        assert sessions == {}

def test_get_sessions_empty():
    """Test handling of no active containers."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""

        sessions = DockerService().get_sessions()
        assert sessions == {}
