import time
import os
import signal
import logging
import threading
from app.config import Config
from app.services.discovery import DiscoveryService

logger = logging.getLogger(__name__)

class MonitorService:
    """Background service that monitors session activity and handles auto-shutdown."""

    @staticmethod
    def start():
        """Starts the monitor thread if enabled in config."""
        if Config.HUB_AUTO_SHUTDOWN:
            thread = threading.Thread(target=MonitorService._monitor_loop, daemon=True)
            thread.start()
            logger.info("Auto-shutdown monitor started (60s timeout).")

    @staticmethod
    def _monitor_loop():
        """Main loop for the monitor thread."""
        last_active = time.time()
        timeout = 60 # Seconds

        while True:
            try:
                last_active = MonitorService.check_and_shutdown(last_active, timeout)
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            time.sleep(10)

    @staticmethod
    def check_and_shutdown(last_active: float, timeout: int) -> float:
        """Performs a single activity check and kills process if stale."""
        try:
            discovery = DiscoveryService()
            sessions = discovery.get_sessions()
        except Exception as e:
            logger.error(f"Discovery failed in monitor: {e}")
            return last_active
        
        # A session is active if it's either local (running) or remote (reachable)
        active_sessions = [
            s for s in sessions 
            if s.get("is_running") or s.get("is_reachable")
        ]

        now = time.time()
        if active_sessions:
            return now
        
        idle_time = now - last_active
        if idle_time > timeout:
            logger.warning(f"Inactivity limit ({timeout}s) reached. Shutting down.")
            os.kill(os.getpid(), signal.SIGTERM)
        
        return last_active
