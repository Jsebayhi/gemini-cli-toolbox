import pytest
from unittest.mock import MagicMock, patch
from app.services.discovery import DiscoveryService
from app.models.session import GeminiSession
from app.services.base import DiscoveryProvider

@pytest.fixture(autouse=True)
def reset_discovery_singleton():
    """Ensure each test has its own DiscoveryService instance."""
    DiscoveryService._instance = None
    yield
    DiscoveryService._instance = None

def test_discovery_provider_base_is_available():
    """Verify default is_available returns True in base class."""
    class MockProvider(DiscoveryProvider):
        def get_sessions(self): return {}
    
    assert MockProvider().is_available() is True

def test_session_to_dict_enrichment():
    """Verify all new fields are in the dict."""
    s = GeminiSession("gem-full", "p", "c", "u1")
    s.is_running = True
    s.is_reachable = True
    s.ip = "1.2.3.4"
    s.local_url = "http://localhost:3000"
    
    d = s.to_dict()
    assert d["is_running"] is True
    assert d["is_reachable"] is True
    assert d["ip"] == "1.2.3.4"
    assert d["local_url"] == "http://localhost:3000"
    assert d["online"] is True

def test_discovery_sorting_alphabetical():
    """Ensure sessions are returned in alphabetical order by name."""
    s_z = GeminiSession("gem-z-last", "p", "c", "u1")
    s_a = GeminiSession("gem-a-first", "p", "c", "u1")
    
    mock_p = MagicMock()
    mock_p.get_sessions.return_value = {s_z.name: s_z, s_a.name: s_a}
    mock_p.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p])
    sessions = service.get_sessions()
    
    names = [s["name"] for s in sessions]
    assert names == ["gem-a-first", "gem-z-last"]

def test_discovery_merging_priority_docker_local_url():
    """Verify that Docker local_url takes precedence."""
    s_docker = GeminiSession("gem-priority", "p", "c", "u1")
    s_docker.local_url = "http://localhost:32768"
    
    s_ts = GeminiSession("gem-priority", "p", "c", "u1")
    s_ts.local_url = "http://remote-url"
    
    mock_p1 = MagicMock()
    mock_p1.get_sessions.return_value = {s_docker.name: s_docker}
    mock_p1.is_available.return_value = True
    
    mock_p2 = MagicMock()
    mock_p2.get_sessions.return_value = {s_ts.name: s_ts}
    mock_p2.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert sessions[0]["local_url"] == "http://localhost:32768"

def test_discovery_provider_failure_graceful():
    """Verify that a provider failure doesn't crash the orchestrator."""
    mock_bad = MagicMock()
    mock_bad.get_sessions.side_effect = Exception("Crashed")
    mock_bad.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_bad])
    assert service.get_sessions() == []

def test_session_online_property_logic():
    """Verify 'online' property behavior."""
    s = GeminiSession("gem-test", "p", "c", "u1")
    s.is_running = False
    s.is_reachable = False
    assert s.online is False
    
    s.is_running = True
    assert s.online is True

def test_discovery_remote_only_session():
    """Verify that sessions only in Tailscale are correctly added."""
    s_ts = GeminiSession("gem-remote-only", "p", "c", "u1")
    s_ts.is_reachable = True
    s_ts.ip = "100.64.0.5"
    
    mock_docker = MagicMock()
    mock_docker.get_sessions.return_value = {} # Empty local
    mock_docker.is_available.return_value = True
    
    mock_ts = MagicMock()
    mock_ts.get_sessions.return_value = {s_ts.name: s_ts}
    mock_ts.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_docker, mock_ts])
    sessions = service.get_sessions()
    
    assert len(sessions) == 1
    assert sessions[0]["name"] == "gem-remote-only"
    assert sessions[0]["is_reachable"] is True
    assert sessions[0]["ip"] == "100.64.0.5"

def test_discovery_ip_enrichment_merging():
    """Verify that IP is added to existing session if missing."""
    s1 = GeminiSession("gem-shared", "p", "c", "u1")
    s1.is_running = True
    # No IP
    
    s2 = GeminiSession("gem-shared", "p", "c", "u1")
    s2.is_reachable = True
    s2.ip = "100.64.0.10"
    
    mock_docker = MagicMock()
    mock_docker.get_sessions.return_value = {s1.name: s1}
    mock_docker.is_available.return_value = True
    
    mock_ts = MagicMock()
    mock_ts.get_sessions.return_value = {s2.name: s2}
    mock_ts.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_docker, mock_ts])
    sessions = service.get_sessions()
    
    assert len(sessions) == 1
    assert sessions[0]["is_running"] is True
    assert sessions[0]["is_reachable"] is True
    assert sessions[0]["ip"] == "100.64.0.10"

def test_discovery_simultaneous_flag_merging():
    """Verify that both flags are updated if both providers report them."""
    s1 = GeminiSession("gem-both", "p", "c", "u1")
    s1.is_running = True
    
    s2 = GeminiSession("gem-both", "p", "c", "u1")
    s2.is_reachable = True
    
    mock_p1 = MagicMock()
    mock_p1.get_sessions.return_value = {s1.name: s1}
    mock_p1.is_available.return_value = True
    
    mock_p2 = MagicMock()
    mock_p2.get_sessions.return_value = {s2.name: s2}
    mock_p2.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert sessions[0]["is_running"] is True
    assert sessions[0]["is_reachable"] is True

def test_discovery_flag_additive_logic():
    """Verify that flags are strictly additive (False -> True)."""
    # Baseline session (Offline)
    s_base = GeminiSession("gem-additive", "p", "c", "u1")
    s_base.is_running = False
    s_base.is_reachable = False
    
    # Update 1: Running
    s_run = GeminiSession("gem-additive", "p", "c", "u1")
    s_run.is_running = True
    
    # Update 2: Reachable
    s_reach = GeminiSession("gem-additive", "p", "c", "u1")
    s_reach.is_reachable = True
    
    mock_p1 = MagicMock(); mock_p1.get_sessions.return_value = {s_base.name: s_base}; mock_p1.is_available.return_value = True
    mock_p2 = MagicMock(); mock_p2.get_sessions.return_value = {s_run.name: s_run}; mock_p2.is_available.return_value = True
    mock_p3 = MagicMock(); mock_p3.get_sessions.return_value = {s_reach.name: s_reach}; mock_p3.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2, mock_p3])
    sessions = service.get_sessions()
    
    assert sessions[0]["is_running"] is True
    assert sessions[0]["is_reachable"] is True

def test_discovery_cross_boolean_merging():
    """Verify that True flags from different providers are merged."""
    s1 = GeminiSession("gem-cross", "p", "c", "u1")
    s1.is_running = True
    s1.is_reachable = False
    
    s2 = GeminiSession("gem-cross", "p", "c", "u1")
    s2.is_running = False
    s2.is_reachable = True
    
    mock_p1 = MagicMock(); mock_p1.get_sessions.return_value = {s1.name: s1}; mock_p1.is_available.return_value = True
    mock_p2 = MagicMock(); mock_p2.get_sessions.return_value = {s2.name: s2}; mock_p2.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert sessions[0]["is_running"] is True
    assert sessions[0]["is_reachable"] is True

def test_discovery_local_url_enrichment_merging():
    """Verify that local_url is added to existing session if missing."""
    s1 = GeminiSession("gem-url", "p", "c", "u1")
    s1.is_running = True
    # No local_url
    
    s2 = GeminiSession("gem-url", "p", "c", "u1")
    s2.local_url = "http://localhost:45000"
    
    mock_p1 = MagicMock(); mock_p1.get_sessions.return_value = {s1.name: s1}; mock_p1.is_available.return_value = True
    mock_p2 = MagicMock(); mock_p2.get_sessions.return_value = {s2.name: s2}; mock_p2.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert len(sessions) == 1
    assert sessions[0]["local_url"] == "http://localhost:45000"

def test_discovery_disjoint_provider_merging():
    """Verify that sessions from different providers are both added."""
    s1 = GeminiSession("gem-only-1", "p", "c", "u1")
    s2 = GeminiSession("gem-only-2", "p", "c", "u1")
    
    mock_p1 = MagicMock(); mock_p1.get_sessions.return_value = {s1.name: s1}; mock_p1.is_available.return_value = True
    mock_p2 = MagicMock(); mock_p2.get_sessions.return_value = {s2.name: s2}; mock_p2.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert len(sessions) == 2
    names = [s["name"] for s in sessions]
    assert "gem-only-1" in names
    assert "gem-only-2" in names

def test_discovery_skip_unavailable_provider():
    """Verify that unavailable providers are skipped without calling get_sessions."""
    mock_p = MagicMock()
    mock_p.is_available.return_value = False
    
    service = DiscoveryService(providers=[mock_p])
    sessions = service.get_sessions()
    
    assert sessions == []
    mock_p.get_sessions.assert_not_called()

def test_discovery_get_session_by_name_helper():
    """Verify clean lookup helper returns correct data or None."""
    s1 = GeminiSession("gem-find-me", "p", "c", "u1")
    s1.is_running = True
    
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=[s1.to_dict()]):
        # Found
        res = DiscoveryService.get_session_by_name("gem-find-me")
        assert res is not None
        assert res["name"] == "gem-find-me"
        
        # Not Found
        assert DiscoveryService.get_session_by_name("non-existent") is None

def test_discovery_malformed_provider_data():
    """Verify that malformed data (not a dict) is handled gracefully."""
    mock_bad = MagicMock()
    mock_bad.get_sessions.return_value = ["not", "a", "dict"]
    mock_bad.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_bad])
    assert service.get_sessions() == []

def test_discovery_empty_provider_results():
    """Verify that empty provider results are handled correctly."""
    mock_p = MagicMock()
    mock_p.get_sessions.return_value = {}
    mock_p.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p])
    assert service.get_sessions() == []

def test_discovery_disjoint_provider_merging_full():
    """Verify that sessions from different providers are both added (full sets)."""
    s1 = GeminiSession("gem-only-1", "p", "c", "u1")
    s2 = GeminiSession("gem-only-2", "p", "c", "u1")
    
    mock_p1 = MagicMock(); mock_p1.get_sessions.return_value = {s1.name: s1}; mock_p1.is_available.return_value = True
    mock_p2 = MagicMock(); mock_p2.get_sessions.return_value = {s2.name: s2}; mock_p2.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert len(sessions) == 2
    names = sorted([s["name"] for s in sessions])
    assert names == ["gem-only-1", "gem-only-2"]

def test_discovery_provider_resilience():
    """Verify that malformed data or exceptions in merging loop are handled."""
    mock_p = MagicMock()
    mock_p.get_sessions.return_value = {"invalid": None}
    mock_p.is_available.return_value = True
    
    service = DiscoveryService(providers=[mock_p])
    assert service.get_sessions() == []
