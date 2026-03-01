from unittest.mock import patch
from app.services.tailscale import TailscaleService

def test_parse_peers_sidecar_grouping():
    """Test that sidecars are grouped into the parent session."""
    
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "gem-project-a-geminicli-1234",
                "TailscaleIPs": ["100.64.0.1"],
                "Online": True
            }
        }
    }
    
    # gem-project-a has a LAN sidecar
    # gem-project-b is local-only and has a VPN sidecar (added later)
    mock_local_ports = {
        "gem-project-a-geminicli-1234": "http://localhost:32768",
        "gem-project-a-geminicli-1234-lan": None,
        "gem-project-b-bash-5678": "http://localhost:32769",
        "gem-project-b-bash-5678-vpn": None
    }
    
    with patch.object(TailscaleService, "get_local_ports", return_value=mock_local_ports):
        machines = TailscaleService.parse_peers(mock_status)
        
        # Should have 2 parent machines, NO sidecars in top level
        assert len(machines) == 2
        assert all(not m["name"].endswith("-vpn") and not m["name"].endswith("-lan") for m in machines)
        
        # Machine A: local + vpn (from TS) + lan (from sidecar)
        a = next(m for m in machines if m["name"] == "gem-project-a-geminicli-1234")
        assert "local" in a["tiers"]
        assert "vpn" in a["tiers"]
        assert "lan" in a["tiers"]
        
        # Machine B: local + vpn (from sidecar)
        b = next(m for m in machines if m["name"] == "gem-project-b-bash-5678")
        assert "local" in b["tiers"]
        assert "vpn" in b["tiers"]
        assert "lan" not in b["tiers"]

def test_parse_peers_metadata_variants():
    """Test metadata extraction for various naming schemes."""
    mock_local_ports = {
        "gem-legacy-proj-abc": None,      # 3 parts
        "gem-my-proj-cli-123-lan": None,  # Sidecar
        "some-random-container": None     # Non-gem
    }
    with patch.object(TailscaleService, "get_local_ports", return_value=mock_local_ports):
        machines = TailscaleService.parse_peers({})
        
        # 1. Legacy name (treated as standard 4-part if possible)
        m1 = next(m for m in machines if m["name"] == "gem-legacy-proj-abc")
        assert m1["project"] == "legacy"
        assert m1["type"] == "proj"
        
        # 2. Sidecar grouping (Parent of the -lan)
        # Should have created a parent entry for gem-my-proj-cli-123
        m2 = next(m for m in machines if m["name"] == "gem-my-proj-cli-123")
        assert m2["project"] == "my-proj"
        assert m2["type"] == "cli"
        assert "lan" in m2["tiers"]

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
        assert "local" in m["tiers"]
