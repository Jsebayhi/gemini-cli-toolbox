from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService


def test_discovery_service_integration_full_stack():
    """
    Trophy: Integration Test (The Bulk).
    Verifies that DiscoveryService correctly orchestrates multiple real 
    provider implementations when OS-level boundaries are mocked.
    """
    # 1. Mock Docker Boundary (OS)
    docker_ps_output = "gem-local-cli-1|127.0.0.1:32768->3000/tcp"
    
    # 2. Mock Tailscale Boundary (OS)
    tailscale_status = {
        "Peer": {
            "n1": {
                "HostName": "gem-local-cli-1",
                "TailscaleIPs": ["100.64.0.1"],
                "Online": True
            },
            "n2": {
                "HostName": "gem-remote-bash-2",
                "TailscaleIPs": ["100.64.0.2"],
                "Online": True
            }
        }
    }

    # Execute full stack orchestration
    with patch("subprocess.run") as mock_run, \
         patch("os.path.exists", return_value=True), \
         patch("json.loads", return_value=tailscale_status), \
         patch("app.services.docker.DockerService.is_available", return_value=True), \
         patch("app.services.tailscale.TailscaleService.is_available", return_value=True):
        
        # side_effect returns for Docker then Tailscale
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=docker_ps_output), # Docker ps
            MagicMock(returncode=0, stdout="{}")             # Tailscale (json.loads handles it)
        ]
        
        sessions = DiscoveryService().get_sessions()
        
        # Verify Orchestration Outcome
        assert len(sessions) == 2
        
        # Hybrid session verified
        s_hybrid = next(s for s in sessions if s["name"] == "gem-local-cli-1")
        assert s_hybrid["is_running"] is True
        assert s_hybrid["is_reachable"] is True
        assert s_hybrid["local_url"] == "http://localhost:32768"
        assert s_hybrid["ip"] == "100.64.0.1"
        
        # Remote session verified
        s_remote = next(s for s in sessions if s["name"] == "gem-remote-bash-2")
        assert s_remote["is_running"] is False
        assert s_remote["is_reachable"] is True
        assert s_remote["ip"] == "100.64.0.2"
