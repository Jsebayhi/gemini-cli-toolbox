import subprocess
from unittest.mock import patch
from app.services.launcher import LauncherService

def test_launch_selective_vpn():
    """Test launching with VPN enabled from a potentially localhost hub."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]), \
             patch("app.config.Config.TAILSCALE_AUTH_KEY", "tskey-123"):
            
            # 1. VPN Enabled
            LauncherService.launch("/mock/root/p1", vpn_enabled=True)
            args, _ = mock_run.call_args
            assert "--remote" in args[0]
            assert "--no-vpn" not in args[0]
            
            # 2. VPN Disabled (Default)
            LauncherService.launch("/mock/root/p2", vpn_enabled=False)
            args, _ = mock_run.call_args
            assert "--no-vpn" in args[0]
            assert "--remote" not in args[0]

def test_launch_localhost_access_opt_out():
    """Test opt-out of localhost mapping."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        
        with patch("app.config.Config.HUB_ROOTS", ["/mock/root"]):
            # 1. Localhost Access Disabled
            LauncherService.launch("/mock/root/p1", localhost_access=False)
            args, _ = mock_run.call_args
            assert "--no-localhost" in args[0]
            
            # 2. Localhost Access Enabled (Default)
            LauncherService.launch("/mock/root/p2", localhost_access=True)
            args, _ = mock_run.call_args
            assert "--no-localhost" not in args[0]
