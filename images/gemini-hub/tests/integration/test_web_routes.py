import pytest
from unittest.mock import patch

def test_home_route(client):
    """Test that the homepage renders correctly."""
    mock_machines = [
        {"name": "gem-machine-1", "project": "proj1", "type": "cli", "ip": "100.1.1.1", "online": True},
        {"name": "gem-machine-2", "project": "proj2", "type": "bash", "ip": "100.1.1.2", "online": False},
    ]

    # Patch the service class directly
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}) as mock_status, \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines) as mock_parse:
    
        response = client.get('/')
        
        # Verify mocks were called
        assert mock_status.called
        assert mock_parse.called
        
        assert response.status_code == 200
        content = response.data.decode()
        
        # Verify template rendering
        assert "Gemini Workspace Hub" in content
        # The template displays the project name, not the raw hostname
        assert "proj1" in content
        assert "bash" in content