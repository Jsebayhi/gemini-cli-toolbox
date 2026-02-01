from unittest.mock import patch
from app.services.tailscale import TailscaleService

@patch("app.services.tailscale.TailscaleService.get_local_ports")
def test_parse_peers_standard(mock_get_local_ports):
    """Test parsing of standard gemini-toolbox hostnames."""
    mock_get_local_ports.return_value = {}
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
    assert peers[0]["uid"] == "a1b2"
    assert peers[0]["online"] is True
    assert peers[0]["local_url"] is None

@patch("app.services.tailscale.TailscaleService.get_local_ports")
def test_parse_peers_with_local_url(mock_get_local_ports):
    """Test parsing of peers when a local port is available."""
    # Mock local port discovery
    mock_get_local_ports.return_value = {
        "gem-local-app-geminicli-1234": "http://localhost:3001"
    }
    
    mock_status = {
        "Peer": {
            "node1": {
                "HostName": "gem-local-app-geminicli-1234",
                "TailscaleIPs": ["100.1.2.3"],
                "Online": True
            }
        }
    }
    
    peers = TailscaleService.parse_peers(mock_status)
    assert len(peers) == 1
    assert peers[0]["name"] == "gem-local-app-geminicli-1234"
    assert peers[0]["uid"] == "1234"
    assert peers[0]["local_url"] == "http://localhost:3001"

@patch("app.services.tailscale.TailscaleService.get_local_ports")
def test_parse_peers_bash(mock_get_local_ports):
    """Test parsing of bash session hostnames."""
    mock_get_local_ports.return_value = {}
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
    assert peers[0]["uid"] == "x9y8"

@patch("app.services.tailscale.TailscaleService.get_local_ports")
def test_parse_peers_complex_project(mock_get_local_ports):
    """Test parsing of project names with hyphens."""
    mock_get_local_ports.return_value = {}
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
    assert peers[0]["uid"] == "1234"

@patch("app.services.tailscale.TailscaleService.get_local_ports")
def test_parse_peers_ignore_non_gem(mock_get_local_ports):
    """Test that non-gemini nodes are ignored."""
    mock_get_local_ports.return_value = {}
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
