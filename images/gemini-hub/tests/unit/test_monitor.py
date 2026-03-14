from unittest.mock import patch
from app.services.monitor import MonitorService
from app.config import Config

# We no longer test the background loop directly in unit tests to avoid thread leaks.
# Core logic is tested in test_monitor_logic.py via check_and_shutdown.

def test_monitor_shutdown_disabled():
    """Ensure monitor handles disabled state gracefully."""
    with patch.object(Config, "HUB_AUTO_SHUTDOWN", False):
        # Should return immediately without starting thread
        with patch("threading.Thread") as mock_thread:
            MonitorService.start()
            mock_thread.assert_not_called()
