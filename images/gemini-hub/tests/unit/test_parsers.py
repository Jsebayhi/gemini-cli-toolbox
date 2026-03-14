import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService
from app.models.session import GeminiSession

@pytest.fixture(autouse=True)
def reset_discovery_singleton():
    """Ensure each test has its own DiscoveryService instance."""
    DiscoveryService._instance = None
    yield
    DiscoveryService._instance = None

def test_discovery_sessions_standard():
    """Test standard session identification and parsing via DiscoveryService."""
    s1_docker = GeminiSession("gem-myproject-geminicli-1", "myproject", "geminicli", "1")
    s1_docker.is_running = True
    s1_docker.local_url = "http://localhost:32768"
    
    s1_remote = GeminiSession("gem-myproject-geminicli-1", "myproject", "geminicli", "1")
    s1_remote.is_reachable = True
    s1_remote.ip = "100.64.0.1"
    
    with patch("app.services.docker.DockerService.get_sessions", return_value={s1_docker.name: s1_docker}), \
         patch("app.services.docker.DockerService.is_available", return_value=True), \
         patch("app.services.tailscale.TailscaleService.get_sessions", return_value={s1_remote.name: s1_remote}), \
         patch("app.services.tailscale.TailscaleService.is_available", return_value=True):
        
        sessions = DiscoveryService.get_sessions()
        assert len(sessions) == 1
        s = sessions[0]
        assert s["project"] == "myproject"
        assert s["is_running"] is True
        assert s["is_reachable"] is True
        assert s["local_url"] == "http://localhost:32768"
        assert s["ip"] == "100.64.0.1"

def test_discovery_sessions_complex_project():
    """Test project names with multiple hyphens."""
    s = GeminiSession("gem-my-cool-project-bash-123", "my-cool-project", "bash", "123")
    s.is_running = True
    
    with patch("app.services.docker.DockerService.get_sessions", return_value={s.name: s}), \
         patch("app.services.docker.DockerService.is_available", return_value=True), \
         patch("app.services.tailscale.TailscaleService.get_sessions", return_value={}), \
         patch("app.services.tailscale.TailscaleService.is_available", return_value=True):
        
        sessions = DiscoveryService.get_sessions()
        assert len(sessions) == 1
        assert sessions[0]["project"] == "my-cool-project"
        assert sessions[0]["type"] == "bash"
