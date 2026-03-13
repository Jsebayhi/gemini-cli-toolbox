import pytest
from unittest.mock import patch
from app.services.discovery import DiscoveryService

@pytest.fixture
def mock_tailscale_status():
    return {
        "Peer": {
            "node1": {
                "HostName": "gem-project-cli-u1",
                "TailscaleIPs": ["100.64.0.1"],
                "Online": True
            },
            "node2": {
                "HostName": "gem-remote-bash-u2",
                "TailscaleIPs": ["100.64.0.2"],
                "Online": False
            }
        }
    }

@pytest.fixture
def mock_docker_ports():
    return {
        "gem-project-cli-u1": "http://localhost:32768",
        "gem-local-only-bash-u3": "http://localhost:45000"
    }

def test_discovery_unified_sessions(mock_tailscale_status, mock_docker_ports):
    """Test DiscoveryService merging of Docker and Tailscale data."""
    with patch("app.services.docker.DockerService.get_local_ports", return_value=mock_docker_ports), \
         patch("app.services.tailscale.TailscaleService.get_status", return_value=mock_tailscale_status):
        
        sessions = DiscoveryService.get_sessions()
        
        # 3 Sessions expected
        assert len(sessions) == 3
        
        # 1. Local Only (Docker)
        m_local = next(s for s in sessions if s["name"] == "gem-local-only-bash-u3")
        assert m_local["project"] == "local-only"
        assert m_local["local_url"] == "http://localhost:45000"
        assert m_local["ip"] is None

        # 2. Hybrid (Both)
        m_hybrid = next(s for s in sessions if s["name"] == "gem-project-cli-u1")
        assert m_hybrid["local_url"] == "http://localhost:32768"
        assert m_hybrid["ip"] == "100.64.0.1"

        # 3. Remote Only (Tailscale)
        m_remote = next(s for s in sessions if s["name"] == "gem-remote-bash-u2")
        assert m_remote["local_url"] is None
        assert m_remote["ip"] == "100.64.0.2"
