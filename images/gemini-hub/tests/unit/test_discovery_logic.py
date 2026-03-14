import pytest
from unittest.mock import MagicMock
from app.services.discovery import DiscoveryService
from app.models.session import GeminiSession

@pytest.fixture(autouse=True)
def reset_discovery_singleton():
    """Ensure each test has its own DiscoveryService instance."""
    DiscoveryService._instance = None
    yield
    DiscoveryService._instance = None

def test_discovery_malformed_provider_data():
    """Trophy: Unit Test (Precision). Hits error branches when providers return junk."""
    mock_bad = MagicMock()
    # Provider returns a list instead of a dict mapping names to sessions
    mock_bad.get_sessions.return_value = ["junk"]
    
    service = DiscoveryService(providers=[mock_bad])
    # Should handle the AttributeError/TypeError gracefully and return empty list
    sessions = service.get_sessions()
    assert sessions == []

def test_discovery_disjoint_provider_merging():
    """Trophy: Unit Test (Precision). Hits 'name not in master_map' branches."""
    s1 = GeminiSession("gem-only-1", "p", "c", "u1")
    s2 = GeminiSession("gem-only-2", "p", "c", "u1")
    
    mock_p1 = MagicMock()
    mock_p1.get_sessions.return_value = {s1.name: s1}
    
    mock_p2 = MagicMock()
    mock_p2.get_sessions.return_value = {s2.name: s2}
    
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert len(sessions) == 2
    names = [s["name"] for s in sessions]
    assert "gem-only-1" in names
    assert "gem-only-2" in names

def test_session_online_property_logic():
    """Trophy: Unit Test (Precision). Hits every branch of the 'online' property."""
    s = GeminiSession("gem-test", "p", "c", "u1")
    
    # 1. Both False -> Offline
    s.is_running = False
    s.is_reachable = False
    assert s.online is False
    
    # 2. Running Only -> Online
    s.is_running = True
    s.is_reachable = False
    assert s.online is True
    
    # 3. Reachable Only -> Online
    s.is_running = False
    s.is_reachable = True
    assert s.online is True
    
    # 4. Both True -> Online
    s.is_running = True
    s.is_reachable = True
    assert s.online is True

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
    s_m = GeminiSession("gem-m-middle", "p", "c", "u1")
    
    mock_docker = MagicMock()
    mock_docker.get_sessions.return_value = {
        s_z.name: s_z,
        s_a.name: s_a,
        s_m.name: s_m
    }
    
    # DiscoveryService sorts results before returning
    service = DiscoveryService(providers=[mock_docker])
    sessions = service.get_sessions()
    
    names = [s["name"] for s in sessions]
    assert names == ["gem-a-first", "gem-m-middle", "gem-z-last"]

def test_discovery_case_sensitivity_merging():
    """Verify that merging handles identical names with different cases if they happen."""
    s1 = GeminiSession("gem-TEST", "p", "c", "u1")
    s1.is_running = True
    
    s2 = GeminiSession("gem-test", "p", "c", "u1")
    s2.is_reachable = True
    
    mock_docker = MagicMock()
    mock_docker.get_sessions.return_value = {s1.name: s1}
    mock_ts = MagicMock()
    mock_ts.get_sessions.return_value = {s2.name: s2}
    
    service = DiscoveryService(providers=[mock_docker, mock_ts])
    sessions = service.get_sessions()
    
    # Should be 2 sessions if case differs, but we verify they are both preserved
    # (The current implementation is case-sensitive for the map keys)
    assert len(sessions) == 2
