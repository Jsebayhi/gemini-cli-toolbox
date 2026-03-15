import pytest
from unittest.mock import patch
import signal
from app.services.monitor import MonitorService
from app.config import Config

@pytest.fixture(autouse=True)
def mock_monitor_deps():
    """Ensure all tests have stable, non-interfering mocks."""
    with patch("time.time", return_value=2000), \
         patch("os.getpid", return_value=1234), \
         patch("os.kill") as mock_kill:
        yield mock_kill

def test_monitor_activity_permutations(mock_monitor_deps):
    """Verify that any activity (local or remote) prevents shutdown."""
    scenarios = [
        (True, False, 2000, False), # Local only -> Active, No Kill
        (False, True, 2000, False), # Remote only -> Active, No Kill
        (True, True, 2000, False),  # Both -> Active, No Kill
        (False, False, 1000, True)  # None -> Remains Idle, TRIGGER KILL
    ]
    
    for running, reachable, expected, should_kill in scenarios:
        mock_monitor_deps.reset_mock()
        mock_sessions = [{"is_running": running, "is_reachable": reachable}]
        with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=mock_sessions):
            res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
            assert res == expected, f"Failed for {running}/{reachable}"
            if should_kill:
                mock_monitor_deps.assert_called_once()
            else:
                mock_monitor_deps.assert_not_called()

def test_monitor_shutdown_trigger(mock_monitor_deps):
    """Verify that SIGTERM is sent exactly when the timeout is exceeded."""
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=[]), \
         patch("time.time", return_value=1061):
        
        # 1061 - 1000 = 61s > 60s
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 1000
        mock_monitor_deps.assert_called_once_with(1234, signal.SIGTERM)

def test_monitor_loop_resilience():
    """Ensure the monitor loop survives a discovery failure."""
    with patch("app.services.monitor.MonitorService.check_and_shutdown", side_effect=[Exception("Discovery Error"), Exception("Stop")]), \
         patch("time.sleep", side_effect=[None, Exception("Stop loop")]), \
         patch("logging.Logger.error") as mock_log:
        
        try:
            MonitorService._monitor_loop()
        except Exception as e:
            if str(e) != "Stop loop":
                raise e
        
        assert mock_log.called

def test_monitor_empty_sessions_idle(mock_monitor_deps):
    """Ensure no sessions results in idle status (no update to last_active)."""
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=[]), \
         patch("time.time", return_value=1050): # 1050 - 1000 = 50s (Still Idle, not stale)
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 1000 # Unchanged
        mock_monitor_deps.assert_not_called()

def test_monitor_online_hybrid_status(mock_monitor_deps):
    """Verify that being 'online' (either flag) prevents idle."""
    # Scenario: Offline on VPN, but Running locally
    mock_sessions = [{"is_running": True, "is_reachable": False}]
    with patch("app.services.discovery.DiscoveryService.get_sessions", return_value=mock_sessions), \
         patch("time.time", return_value=3000):
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 3000 # Updated
        mock_monitor_deps.assert_not_called()

def test_monitor_start_logic_enabled():
    """Verify monitor starts when enabled."""
    with patch.object(Config, "HUB_AUTO_SHUTDOWN", True), \
         patch("threading.Thread") as mock_thread:
        MonitorService.start()
        assert mock_thread.call_count == 1
        assert mock_thread.call_args[1]["target"] == MonitorService._monitor_loop

def test_monitor_start_logic_disabled():
    """Verify monitor skips when disabled."""
    with patch.object(Config, "HUB_AUTO_SHUTDOWN", False), \
         patch("threading.Thread") as mock_thread:
        MonitorService.start()
        assert mock_thread.call_count == 0

def test_monitor_check_and_shutdown_discovery_failure():
    """Verify that monitor handles discovery failure gracefully (no state update)."""
    with patch("app.services.discovery.DiscoveryService.get_sessions") as mock_get:
        mock_get.side_effect = Exception("Discovery Crashed")
        
        # Should catch exception and return the original last_active
        res = MonitorService.check_and_shutdown(last_active=1000, timeout=60)
        assert res == 1000

def test_monitor_loop_iteration_timing():
    """Trophy: Unit Test (Precision). Hits loop iteration and logging."""
    # We mock the loop to run once then raise to exit
    with patch("app.services.monitor.MonitorService.check_and_shutdown") as mock_check, \
         patch("time.sleep", side_effect=[None, Exception("Exit Loop")]) as mock_sleep, \
         patch("logging.Logger.error"):
        
        mock_check.return_value = 1000
        
        try:
            MonitorService._monitor_loop()
        except Exception as e:
            if str(e) != "Exit Loop":
                raise e
        
        assert mock_check.call_count >= 1
        assert mock_sleep.call_count >= 1
