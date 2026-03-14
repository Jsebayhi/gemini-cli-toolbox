from unittest.mock import patch
import signal
from app.services.monitor import MonitorService
from app.config import Config

def test_monitor_check_active():
    """Test that check_and_shutdown returns 'now' if sessions are active (local)."""
    # Local 'running' session
    mock_sessions = [{
        "name": "gem-1", 
        "is_running": True,
        "is_reachable": False,
        "online": True
    }]
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=mock_sessions), \
         patch("time.time", return_value=2000):
        
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 2000

def test_monitor_check_active_remote():
    """Test that reachable remote sessions count as activity."""
    # Remote 'reachable' session
    mock_sessions = [{
        "name": "gem-remote", 
        "is_running": False,
        "is_reachable": True,
        "online": True
    }]
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=mock_sessions), \
         patch("time.time", return_value=2000):
        
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 2000

def test_monitor_check_idle_safe():
    """Test that check_and_shutdown returns 'last_active' if idle but safe."""
    mock_sessions = []
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=mock_sessions), \
         patch("time.time", return_value=1030): # Only 30s passed
        
        # Should return 'last_active' (1000)
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 1000

def test_monitor_check_stale_shutdown():
    """Test that check_and_shutdown triggers kill if stale."""
    mock_sessions = []
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=mock_sessions), \
         patch("time.time", return_value=1100), \
         patch("os.kill") as mock_kill:
        
        # Should call kill
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 1000
        mock_kill.assert_called_once()
        assert mock_kill.call_args[0][1] == signal.SIGTERM

def test_monitor_start_disabled():
    """Ensure monitor doesn't start if auto-shutdown is disabled."""
    with patch.object(Config, "HUB_AUTO_SHUTDOWN", False), \
         patch("threading.Thread") as mock_thread:
        MonitorService.start()
        mock_thread.assert_not_called()

def test_monitor_start_enabled():
    """Ensure monitor starts if enabled."""
    with patch.object(Config, "HUB_AUTO_SHUTDOWN", True), \
         patch("threading.Thread") as mock_thread:
        MonitorService.start()
        mock_thread.assert_called_once()

def test_monitor_loop_exception_handling():
    """Test that the monitor loop continues after a provider error."""
    with patch("app.services.monitor.MonitorService.check_and_shutdown", side_effect=[Exception("Check failed"), Exception("Stop")]), \
         patch("time.sleep", side_effect=[None, Exception("Stop loop")]), \
         patch("logging.Logger.error") as mock_log:
        
        try:
            MonitorService._monitor_loop()
        except Exception:
            pass
        
        # Should have logged the first error and continued to sleep
        assert mock_log.called
