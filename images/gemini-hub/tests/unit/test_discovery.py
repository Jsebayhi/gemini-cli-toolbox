import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService

def test_get_local_containers_failures():
    with patch("subprocess.run") as mock_run:
        # 1. Command failure
        mock_run.return_value = MagicMock(returncode=1)
        assert DiscoveryService.get_local_containers() == []
        
        # 2. Exception
        mock_run.side_effect = Exception("Boom")
        assert DiscoveryService.get_local_containers() == []

def test_get_local_containers_edge_cases():
    # 1. Line without pipe
    # 2. Non-gem container
    # 3. Malformed ports (no colon)
    # 4. Short hostname (gem-proj-uid)
    mock_ps_output = "malformed_line\nnon-gem-container|80->80/tcp|Up\ngem-proj-uid|80->3000/tcp|Up\ngem-valid-cli-uid|malformed_ports|Up"
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_ps_output)
        containers = DiscoveryService.get_local_containers()
        assert len(containers) == 2
        
        # Check short hostname parsing (len parts == 3)
        c_short = next(c for c in containers if c["name"] == "gem-proj-uid")
        assert c_short["project"] == "proj"
        assert c_short["type"] == "cli"
        assert c_short["local_url"] is None # No colon in "80"

def test_get_status_failures():
    with patch("subprocess.run") as mock_run:
        # 1. Command failure
        mock_run.return_value = MagicMock(returncode=1)
        assert DiscoveryService.get_status() == {}
        
        # 2. Exception
        mock_run.side_effect = Exception("Boom")
        assert DiscoveryService.get_status() == {}

def test_parse_peers_remote_types():
    # Test remote session with 4 parts in name
    mock_ts_status = {
        "Peer": {
            "node": {"HostName": "gem-my-proj-bash-uid", "TailscaleIPs": ["100.64.0.1"], "Online": True}
        }
    }
    with patch.object(DiscoveryService, "get_local_containers", return_value=[]):
        machines = DiscoveryService.parse_peers(mock_ts_status)
        assert len(machines) == 1
        assert machines[0]["project"] == "my-proj"
        assert machines[0]["type"] == "bash"
    # 1 local container (also in Tailscale)
    # 1 remote peer (only in Tailscale)
    # 1 local container (not in Tailscale)
    
    mock_local = [
        {"name": "gem-local-vpn-uid", "project": "local", "type": "vpn", "uid": "uid", "local_url": "http://localhost:3000", "online": True},
        {"name": "gem-only-local-uid", "project": "only", "type": "local", "uid": "uid", "local_url": "http://localhost:3001", "online": True}
    ]
    
    mock_ts_status = {
        "Peer": {
            "node1": {"HostName": "gem-local-vpn-uid", "TailscaleIPs": ["100.64.0.1"], "Online": True},
            "node2": {"HostName": "gem-remote-uid", "TailscaleIPs": ["100.64.0.2"], "Online": True}
        }
    }
    
    with patch.object(DiscoveryService, "get_local_containers", return_value=mock_local):
        machines = DiscoveryService.parse_peers(mock_ts_status)
        
        assert len(machines) == 3
        
        # Check Local + VPN
        m1 = next(m for m in machines if m["name"] == "gem-local-vpn-uid")
        assert m1["is_local"] is True
        assert m1["has_vpn"] is True
        assert m1["ip"] == "100.64.0.1"
        
        # Check Local only
        m2 = next(m for m in machines if m["name"] == "gem-only-local-uid")
        assert m2["is_local"] is True
        assert m2["has_vpn"] is False
        assert m2["ip"] == "127.0.0.1"
        
        # Check Remote only
        m3 = next(m for m in machines if m["name"] == "gem-remote-uid")
        assert m3["is_local"] is False
        assert m3["has_vpn"] is True
        assert m3["ip"] == "100.64.0.2"
