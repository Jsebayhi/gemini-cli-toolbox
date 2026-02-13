import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService

def test_get_local_containers():
    mock_ps_output = "gem-proj-cli-uid1|127.0.0.1:32768->3000/tcp|Up 5 minutes\ngem-proj2-bash-uid2|127.0.0.1:32769->3000/tcp|Up 10 minutes"
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_ps_output)
        
        containers = DiscoveryService.get_local_containers()
        
        assert len(containers) == 2
        assert containers[0]["name"] == "gem-proj-cli-uid1"
        assert containers[0]["local_url"] == "http://localhost:32768"
        assert containers[1]["project"] == "proj2"
        assert containers[1]["type"] == "bash"

def test_parse_peers_unified():
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
