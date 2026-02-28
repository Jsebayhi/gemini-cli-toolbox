from unittest.mock import patch
from app.services.tailscale import TailscaleService

def test_parse_peers_unified_discovery():
    """Test unified discovery combining Tailscale and Local containers."""
    
    # 1. Mock Tailscale Status (one peer)
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "gem-project-a-geminicli-1234",
                "TailscaleIPs": ["100.64.0.1"],
                "Online": True
            }
        }
    }
    
    # 2. Mock Local Ports (two containers)
    # project-a is also in Tailscale (Hybrid)
    # project-b is ONLY local (Local-only)
    mock_local_ports = {
        "gem-project-a-geminicli-1234": "http://localhost:32768",
        "gem-project-b-bash-5678": "http://localhost:32769"
    }
    
    with patch.object(TailscaleService, "get_local_ports", return_value=mock_local_ports):
        machines = TailscaleService.parse_peers(mock_status)
        
        # Should have 2 machines
        assert len(machines) == 2
        
        # Machine A: Hybrid
        a = next(m for m in machines if m["name"] == "gem-project-a-geminicli-1234")
        assert a["ip"] == "100.64.0.1"
        assert a["local_url"] == "http://localhost:32768"
        assert a["project"] == "project-a"
        assert a["type"] == "geminicli"
        
        # Machine B: Local-only
        b = next(m for m in machines if m["name"] == "gem-project-b-bash-5678")
        assert b["ip"] is None
        assert b["local_url"] == "http://localhost:32769"
        assert b["project"] == "project-b"
        assert b["type"] == "bash"
        assert b["online"] is True

def test_parse_peers_no_tailscale():
    """Test discovery when Tailscale returns no peers or fails."""
    
    mock_status = {} # Empty or failed status
    mock_local_ports = {
        "gem-project-c-geminicli-9012": "http://localhost:32770"
    }
    
    with patch.object(TailscaleService, "get_local_ports", return_value=mock_local_ports):
        machines = TailscaleService.parse_peers(mock_status)
        
        assert len(machines) == 1
        m = machines[0]
        assert m["name"] == "gem-project-c-geminicli-9012"
        assert m["ip"] is None
        assert m["local_url"] == "http://localhost:32770"
        assert m["online"] is True
