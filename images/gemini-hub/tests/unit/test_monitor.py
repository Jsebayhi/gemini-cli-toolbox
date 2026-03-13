import pytest
from unittest.mock import patch
from app.services.monitor import MonitorService

def test_monitor_shutdown_trigger():
    """Test that monitor triggers shutdown after timeout."""
    # Mock Config to enable shutdown
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("app.services.monitor.DiscoveryService") as MockDiscovery, \
         patch("app.services.monitor.os.kill") as mock_kill, \
         patch("app.services.monitor.time") as mock_time:
        
        MockConfig.HUB_AUTO_SHUTDOWN = True
        # Mock no machines found (idle)
        MockDiscovery.get_sessions.return_value = []
        
        # Simulate time passing (exceeding 60s timeout)
        mock_time.time.side_effect = [100, 170]
        
        # We only want one iteration of the loop for the test
        with patch("time.sleep", side_effect=InterruptedError):
            try:
                MonitorService._monitor_loop()
            except InterruptedError:
                pass
        
        # Verify kill was called
        mock_kill.assert_called_once()

def test_monitor_activity_reset():
    """Test that active sessions reset the timer."""
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("app.services.monitor.DiscoveryService") as MockDiscovery, \
         patch("app.services.monitor.os.kill") as mock_kill, \
         patch("app.services.monitor.time") as mock_time:
        
        MockConfig.HUB_AUTO_SHUTDOWN = True
        # Mock active session found
        MockDiscovery.get_sessions.return_value = [{"name": "gem-active"}]
        
        mock_time.time.return_value = 100
        
        with patch("time.sleep", side_effect=InterruptedError):
            try:
                MonitorService._monitor_loop()
            except InterruptedError:
                pass
        
        # Verify kill was NOT called
        mock_kill.assert_not_called()

def test_monitor_shutdown_disabled():
    """Test that monitor doesn't start if auto-shutdown is disabled."""
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("threading.Thread") as mock_thread:
        
        MockConfig.HUB_AUTO_SHUTDOWN = False
        MonitorService.start()
        mock_thread.assert_not_called()

def test_monitor_exception_handling():
    """Test that monitor logs exceptions without crashing."""
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("app.services.monitor.DiscoveryService") as MockDiscovery, \
         patch("app.services.monitor.time") as mock_time, \
         patch("app.services.monitor.logger") as mock_logger:
        
        MockConfig.HUB_AUTO_SHUTDOWN = True
        MockDiscovery.get_sessions.side_effect = Exception("Discovery Error")
        
        mock_time.time.return_value = 100
        
        with patch("time.sleep", side_effect=InterruptedError):
            try:
                MonitorService._monitor_loop()
            except InterruptedError:
                pass
        
        # Verify error was logged
        mock_logger.error.assert_called()
