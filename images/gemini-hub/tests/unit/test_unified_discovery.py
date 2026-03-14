import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService
from app.models.session import GeminiSession

@pytest.fixture
def mock_tailscale_sessions():
    s1 = GeminiSession("gem-project-cli-u1", "project", "cli", "u1")
    s1.is_reachable = True
    s1.ip = "100.64.0.1"
    
    s2 = GeminiSession("gem-remote-bash-u2", "remote", "bash", "u2")
    s2.is_reachable = False # Known but offline
    s2.ip = "100.64.0.2"
    
    return {s1.name: s1, s2.name: s2}

@pytest.fixture
def mock_docker_sessions():
    s1 = GeminiSession("gem-project-cli-u1", "project", "cli", "u1")
    s1.is_running = True
    s1.local_url = "http://localhost:32768"
    
    s2 = GeminiSession("gem-local-only-bash-u3", "local-only", "bash", "u3")
    s2.is_running = True
    s2.local_url = "http://localhost:45000"
    
    return {s1.name: s1, s2.name: s2}

def test_discovery_unified_merging(mock_tailscale_sessions, mock_docker_sessions):
    """Test merging and enrichment logic."""
    with patch("app.services.docker.DockerService.get_sessions", return_value=mock_docker_sessions), \
         patch("app.services.tailscale.TailscaleService.get_sessions", return_value=mock_tailscale_sessions):
        
        sessions = DiscoveryService.get_sessions()
        assert len(sessions) == 3
        
        # Hybrid Session (both)
        m_hybrid = next(s for s in sessions if s["name"] == "gem-project-cli-u1")
        assert m_hybrid["is_running"] is True
        assert m_hybrid["is_reachable"] is True
        assert m_hybrid["ip"] == "100.64.0.1"
        assert m_hybrid["local_url"] == "http://localhost:32768"

def test_discovery_provider_failure_handling():
    """Test that one failing provider doesn't break discovery."""
    mock_docker = MagicMock()
    mock_docker.get_sessions.side_effect = Exception("Docker Down")
    
    s1 = GeminiSession("gem-s1-cli-u1", "p", "c", "u1")
    mock_ts = MagicMock()
    mock_ts.get_sessions.return_value = {s1.name: s1}
    
    service = DiscoveryService(providers=[mock_docker, mock_ts])
    sessions = service._get_sessions_internal()
    
    assert len(sessions) == 1
    assert sessions[0]["name"] == "gem-s1-cli-u1"

def test_discovery_sorting():
    """Ensure sessions are returned sorted by name."""
    s_b = GeminiSession("gem-b-cli-u1", "p", "c", "u1")
    s_a = GeminiSession("gem-a-cli-u1", "p", "c", "u1")
    
    mock_prov = MagicMock()
    mock_prov.get_sessions.return_value = {s_b.name: s_b, s_a.name: s_a}
    
    service = DiscoveryService(providers=[mock_prov])
    sessions = service._get_sessions_internal()
    
    assert sessions[0]["name"] == "gem-a-cli-u1"
    assert sessions[1]["name"] == "gem-b-cli-u1"

def test_tailscale_graceful_missing_socket():
    """Test that TailscaleService fails silently if socket is missing."""
    from app.services.tailscale import TailscaleService
    with patch("os.path.exists", return_value=False):
        res = TailscaleService().get_sessions()
        assert res == {}
