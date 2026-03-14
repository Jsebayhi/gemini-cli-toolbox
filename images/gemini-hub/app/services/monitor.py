import time
import os
import signal
import logging
import threading
from app.config import Config
from app.services.discovery import DiscoveryService

logger = logging.getLogger(__name__)

class MonitorService:
    """Background service to monitor activity and auto-shutdown."""

    @staticmethod
    def start():
        """Starts the monitor thread if enabled."""
        if not Config.HUB_AUTO_SHUTDOWN:
            logger.info("Auto-shutdown disabled.")
            return
            
        thread = threading.Thread(target=MonitorService._monitor_loop, daemon=True)
        thread.start()

    @staticmethod
    def _monitor_loop():
        TIMEOUT_SECONDS = 60
        last_active = time.time()
        
        logger.info(f"Monitor started. Auto-shutdown after {TIMEOUT_SECONDS}s of inactivity.")
        
        while True:
            try:
                last_active = MonitorService.check_and_shutdown(last_active, TIMEOUT_SECONDS)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            
            time.sleep(10)

    @staticmethod
    def check_and_shutdown(last_active: float, timeout: int) -> float:
        """Performs a single activity check and kills process if stale."""
        try:
            sessions = DiscoveryService.get_sessions()
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
        else:
            idle_time = now - last_active
            if idle_time > timeout:
                logger.warning(f"Inactivity limit ({timeout}s) reached. Shutting down.")
                os.kill(os.getpid(), signal.SIGTERM)
            return last_active
