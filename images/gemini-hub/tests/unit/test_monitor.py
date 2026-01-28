import pytest
from unittest.mock import patch, MagicMock
from app.services.monitor import MonitorService

def test_monitor_shutdown_trigger():
    """Test that monitor triggers shutdown after timeout."""
    # Mock Config to enable shutdown
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("app.services.monitor.TailscaleService") as MockTailscale, \
         patch("app.services.monitor.os.kill") as mock_kill, \
         patch("app.services.monitor.time") as mock_time:
        
        MockConfig.HUB_AUTO_SHUTDOWN = True
        
        # Scenario: 
        # 1. No machines found (empty list)
        # 2. Time advances beyond timeout (60s)
        MockTailscale.get_status.return_value = {}
        MockTailscale.parse_peers.return_value = []
        
        # Simulation:
        # time.time() called for last_active init -> returns 0
        # loop runs once: time.sleep(10) -> side_effect to break loop after 1 iteration?
        # Actually, since _monitor_loop is infinite, we can't run it directly in test without breaking it.
        # Strategy: Mock time.sleep to raise StopIteration to exit loop? Or test logic by extraction?
        # Since logic is inside _monitor_loop, we'll patch time.sleep to raise an exception after 1 call
        # But we need time.time() to return sequence: 0 (init), 100 (check) 
        
        mock_time.time.side_effect = [0, 100]
        mock_time.sleep.side_effect = [None, StopIteration] # Run once then crash
        
        try:
            MonitorService._monitor_loop()
        except StopIteration:
            pass
            
        # Verify Shutdown Triggered
        assert mock_kill.called
        assert mock_kill.call_args[0][1] == 15 # SIGTERM

def test_monitor_shutdown_disabled():
    """Test that monitor respects configuration."""
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("app.services.monitor.threading.Thread") as MockThread:
        
        MockConfig.HUB_AUTO_SHUTDOWN = False
        MonitorService.start()
        
        # Verify thread NOT started
        assert not MockThread.called

def test_monitor_activity_reset():
    """Test that active peers reset the timer."""
    with patch("app.services.monitor.Config") as MockConfig, \
         patch("app.services.monitor.TailscaleService") as MockTailscale, \
         patch("app.services.monitor.os.kill") as mock_kill, \
         patch("app.services.monitor.time") as mock_time:
        
        MockConfig.HUB_AUTO_SHUTDOWN = True
        
        # Scenario: Peers found
        MockTailscale.get_status.return_value = {}
        MockTailscale.parse_peers.return_value = [{"name": "machine1"}]
        
        mock_time.time.side_effect = [0, 100] # Should reset last_active to 100
        mock_time.sleep.side_effect = [None, StopIteration]
        
        try:
            MonitorService._monitor_loop()
        except StopIteration:
            pass
            
        # Verify NO Shutdown
        assert not mock_kill.called
