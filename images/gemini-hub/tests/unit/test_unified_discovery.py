import pytest
from unittest.mock import patch
from app.services.tailscale import TailscaleService

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
            },
            "node3": {
                "HostName": "gem-project-cli-u1-vpn",
                "TailscaleIPs": ["100.64.0.3"],
                "Online": True
            }
        }
    }

@pytest.fixture
def mock_docker_ports():
    return {
        "gem-project-cli-u1": "http://localhost:32768",
        "gem-local-only-bash-u3": "http://localhost:45000",
        "gem-project-cli-u1-vpn": "http://localhost:0"
    }

def test_parse_peers_unified_discovery(mock_tailscale_status, mock_docker_ports):
    """Test merging of local Docker containers and Tailscale peers (Backend Only)."""
    with patch.object(TailscaleService, "get_local_ports", return_value=mock_docker_ports):
        machines = TailscaleService.parse_peers(mock_tailscale_status)
        
        # Should find 3 primary sessions:
        assert len(machines) == 3
        
        # gem-local-only-bash-u3 (Local Only: Docker Only)
        m_local = next(m for m in machines if m["name"] == "gem-local-only-bash-u3")
        assert m_local["project"] == "local-only"
        assert m_local["online"] is True
        assert "local" in m_local["tiers"]
        assert "vpn" not in m_local["tiers"]

        # gem-project-cli-u1 (Hybrid: Docker + Tailscale)
        m_hybrid = next(m for m in machines if m["name"] == "gem-project-cli-u1")
        assert m_hybrid["local_url"] == "http://localhost:32768"
        assert m_hybrid["ip"] == "100.64.0.1"
        assert m_hybrid["vpn_active"] is True
        assert "local" in m_hybrid["tiers"]
        assert "vpn" in m_hybrid["tiers"]

        # gem-remote-bash-u2 (Remote Only: Tailscale Only)
        m_remote = next(m for m in machines if m["name"] == "gem-remote-bash-u2")
        assert m_remote["local_url"] is None
        assert m_remote["ip"] == "100.64.0.2"
        assert "vpn" in m_remote["tiers"]
