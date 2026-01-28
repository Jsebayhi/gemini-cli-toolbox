from app.services.tailscale import TailscaleService

def test_parse_peers_standard():
    """Test parsing of standard gemini-toolbox hostnames."""
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "gem-myproject-geminicli-a1b2",
                "TailscaleIPs": ["100.1.2.3"],
                "Online": True
            }
        }
    }
    
    peers = TailscaleService.parse_peers(mock_status)
    assert len(peers) == 1
    assert peers[0]["project"] == "myproject"
    assert peers[0]["type"] == "geminicli"
    assert peers[0]["online"] is True

def test_parse_peers_bash():
    """Test parsing of bash session hostnames."""
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "gem-debug-bash-x9y8",
                "TailscaleIPs": ["100.1.2.4"],
                "Online": False
            }
        }
    }
    
    peers = TailscaleService.parse_peers(mock_status)
    assert len(peers) == 1
    assert peers[0]["type"] == "bash"
    assert peers[0]["project"] == "debug"

def test_parse_peers_complex_project():
    """Test parsing of project names with hyphens."""
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "gem-my-complex-app-geminicli-1234",
                "TailscaleIPs": ["100.1.2.5"],
                "Online": True
            }
        }
    }
    
    peers = TailscaleService.parse_peers(mock_status)
    assert len(peers) == 1
    # Project should join parts: "my-complex-app"
    assert peers[0]["project"] == "my-complex-app"
    assert peers[0]["type"] == "geminicli"

def test_parse_peers_ignore_non_gem():
    """Test that non-gemini nodes are ignored."""
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "desktop-pc",
                "TailscaleIPs": ["100.1.2.6"],
                "Online": True
            }
        }
    }
    
    peers = TailscaleService.parse_peers(mock_status)
    assert len(peers) == 0
