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
    
    s3 = GeminiSession("gem-local-only-bash-u3", "local-only", "bash", "u3")
    s3.is_running = True
    s3.local_url = "http://localhost:45000"
    
    return {s1.name: s1, s3.name: s3}

def test_discovery_unified_merging(mock_tailscale_sessions, mock_docker_sessions):
    """
    Trophy: Integration Test (The Bulk).
    Verifies that DiscoveryService correctly merges local and remote results.
    """
    with patch("app.services.docker.DockerService.get_sessions", return_value=mock_docker_sessions), \
         patch("app.services.docker.DockerService.is_available", return_value=True), \
         patch("app.services.tailscale.TailscaleService.get_sessions", return_value=mock_tailscale_sessions), \
         patch("app.services.tailscale.TailscaleService.is_available", return_value=True):
        
        sessions = DiscoveryService().get_sessions()
        assert len(sessions) == 3
        
        # 1. Hybrid Session (both Docker and Tailscale)
        m_hybrid = next(s for s in sessions if s["name"] == "gem-project-cli-u1")
        assert m_hybrid["is_running"] is True
        assert m_hybrid["is_reachable"] is True
        assert m_hybrid["ip"] == "100.64.0.1"
        assert m_hybrid["local_url"] == "http://localhost:32768"
        assert m_hybrid["online"] is True

        # 2. Remote Only
        m_remote = next(s for s in sessions if s["name"] == "gem-remote-bash-u2")
        assert m_remote["is_running"] is False
        assert m_remote["is_reachable"] is False
        assert m_remote["online"] is False

        # 3. Local Only
        m_local = next(s for s in sessions if s["name"] == "gem-local-only-bash-u3")
        assert m_local["is_running"] is True
        assert m_local["is_reachable"] is False
        assert m_local["online"] is True

def test_discovery_provider_failure_resilience():
    """Ensure a crashing provider doesn't sink the entire Hub."""
    # Create mock providers that don't depend on system state
    mock_docker = MagicMock()
    mock_docker.get_sessions.side_effect = Exception("Docker Socket Denied")
    mock_docker.is_available.return_value = True
    
    s1 = GeminiSession("gem-s1-cli-u1", "p", "c", "u1")
    mock_ts = MagicMock()
    mock_ts.get_sessions.return_value = {s1.name: s1}
    mock_ts.is_available.return_value = True
    
    # Instantiate with ONLY these mocks
    service = DiscoveryService(providers=[mock_docker, mock_ts])
    
    # We bypass the static 'get_sessions' singleton to test this specific instance
    sessions = service.get_sessions()
    
    assert len(sessions) == 1
    assert sessions[0]["name"] == "gem-s1-cli-u1"

def test_discovery_exhaustive_merging_branches():
    """Trophy: Unit Test (Precision). Hits every branch in the merging loop."""
    s_docker = GeminiSession("gem-exhaustive", "p", "c", "u1")
    s_docker.is_running = True
    s_docker.local_url = "http://localhost:1234"
    
    s_ts = GeminiSession("gem-exhaustive", "p", "c", "u1")
    s_ts.is_reachable = True
    s_ts.ip = "1.2.3.4"
    
    mock_docker = MagicMock()
    mock_docker.get_sessions.return_value = {s_docker.name: s_docker}
    mock_docker.is_available.return_value = True
    mock_ts = MagicMock()
    mock_ts.get_sessions.return_value = {s_ts.name: s_ts}
    mock_ts.is_available.return_value = True

    service = DiscoveryService(providers=[mock_docker, mock_ts])
    sessions = service.get_sessions()
    
    assert len(sessions) == 1
    s = sessions[0]
    assert s["is_running"] is True
    assert s["is_reachable"] is True
    assert s["ip"] == "1.2.3.4"
    assert s["local_url"] == "http://localhost:1234"
    assert s["online"] is True

def test_discovery_get_session_by_name():
    """Verify clean lookup helper."""
    s1 = GeminiSession("gem-s1-cli-u1", "p", "c", "u1")
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=[s1.to_dict()]):
        res = DiscoveryService.get_session_by_name("gem-s1-cli-u1")
        assert res is not None
        assert res["name"] == "gem-s1-cli-u1"
        
        assert DiscoveryService.get_session_by_name("non-existent") is None
