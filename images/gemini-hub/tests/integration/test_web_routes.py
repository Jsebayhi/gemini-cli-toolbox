from unittest.mock import patch

def test_home_route(client):
    """Test that the homepage renders correctly."""
    mock_machines = [
        {"name": "gem-machine-1", "project": "proj1", "type": "cli", "ip": "100.1.1.1", "online": True},
        {"name": "gem-machine-2", "project": "proj2", "type": "bash", "ip": "100.1.1.2", "online": False},
    ]

    # Patch the discovery service
    with patch("app.web.routes.DiscoveryService.get_sessions", return_value=mock_machines) as mock_get:
    
        response = client.get('/')
        
        # Verify mock was called
        assert mock_get.called
        
        assert response.status_code == 200
        content = response.data.decode()
        
        # Verify template rendering
        assert "Gemini Workspace Hub" in content
        # The template displays the project name, not the raw hostname
        assert "proj1" in content
        assert "bash" in content