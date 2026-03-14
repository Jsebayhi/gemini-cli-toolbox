import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService
from app.services.tailscale import TailscaleService
from app.models.session import GeminiSession
from app.config import Config

@pytest.fixture(autouse=True)
def reset_discovery_singleton():
    """Ensure each test has its own DiscoveryService instance."""
    DiscoveryService._instance = None
    yield
    DiscoveryService._instance = None

# --- Discovery Logic Tests ---

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

# --- Discovery Priority Logic Tests (from test_discovery_priority_logic.py) ---

def test_discovery_merging_priority_docker_local_url():
    """Verify that Docker local_url takes precedence and IP is merged carefully."""
    s_docker = GeminiSession("gem-priority", "p", "c", "u1")
    s_docker.is_running = True
    s_docker.local_url = "http://localhost:32768"
    
    s_ts = GeminiSession("gem-priority", "p", "c", "u1")
    s_ts.is_reachable = True
    s_ts.ip = "100.64.0.1"
    s_ts.local_url = "http://remote-url" # Should be ignored
    
    mock_p1 = MagicMock()
    mock_p1.get_sessions.return_value = {s_docker.name: s_docker}
    mock_p1.is_available.return_value = True
    
    mock_p2 = MagicMock()
    mock_p2.get_sessions.return_value = {s_ts.name: s_ts}
    mock_p2.is_available.return_value = True
    
    # DiscoveryService order matters: Docker then Tailscale
    service = DiscoveryService(providers=[mock_p1, mock_p2])
    sessions = service.get_sessions()
    
    assert len(sessions) == 1
    s = sessions[0]
    assert s["local_url"] == "http://localhost:32768" # Precedence
    assert s["ip"] == "100.64.0.1" # Merged
    assert s["is_running"] is True
    assert s["is_reachable"] is True

def test_discovery_no_vpn_disables_tailscale():
    """Verify that Config.HUB_NO_VPN prevents TailscaleService from being used."""
    with patch.object(Config, "HUB_NO_VPN", True):
        service = DiscoveryService()
        # Should only have DockerService
        from app.services.docker import DockerService
        from app.services.tailscale import TailscaleService
        
        assert any(isinstance(p, DockerService) for p in service.providers)
        assert not any(isinstance(p, TailscaleService) for p in service.providers)

def test_discovery_provider_skips_if_not_available():
    """Verify that DiscoveryService skips unavailable providers."""
    mock_p = MagicMock()
    mock_p.is_available.return_value = False
    
    service = DiscoveryService(providers=[mock_p])
    service.get_sessions()
    
    mock_p.get_sessions.assert_not_called()

# --- Tailscale Logic Tests (from test_tailscale_logic.py) ---

def test_tailscale_is_available_success():
    """Verify is_available returns True if socket exists."""
    with patch("os.path.exists", return_value=True):
        assert TailscaleService().is_available() is True

def test_tailscale_is_available_failure():
    """Verify is_available returns False if socket missing."""
    with patch("os.path.exists", return_value=False):
        assert TailscaleService().is_available() is False

def test_tailscale_get_status_error_handling():
    """Verify get_status handles command errors gracefully."""
    with patch("os.path.exists", return_value=True), \
         patch("subprocess.run") as mock_run:
        # Error return code
        mock_run.return_value.returncode = 1
        assert TailscaleService.get_status() == {}
        
        # Exception during run
        mock_run.side_effect = Exception("OS Error")
        assert TailscaleService.get_status() == {}

def test_tailscale_get_sessions_missing_ip():
    """Verify sessions without IPs are skipped."""
    mock_status = {
        "Peer": {
            "n1": {
                "HostName": "gem-no-ip",
                "TailscaleIPs": [],
                "Online": True
            }
        }
    }
    with patch("app.services.tailscale.TailscaleService.get_status", return_value=mock_status):
        sessions = TailscaleService().get_sessions()
        assert "gem-no-ip" not in sessions
