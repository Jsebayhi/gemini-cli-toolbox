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
        if not Config.HUB_AUTO_SHUTDOWN:
            logger.info("Auto-shutdown disabled.")
            return
            
        if os.environ.get("GEMINI_HUB_TEST_MODE") == "true":
            logger.info("Test mode detected. Monitor thread suppressed.")
            return

        thread = threading.Thread(target=MonitorService._monitor_loop, daemon=True)
        thread.start()

    @staticmethod
    def _monitor_loop():
        TIMEOUT_SECONDS = 60
        last_active = time.time()
        
        logger.info(f"Monitor started. Auto-shutdown after {TIMEOUT_SECONDS}s of inactivity.")
        
        while True:
            time.sleep(10)
            try:
                # Check for active sessions using Unified Discovery
                machines = DiscoveryService.get_sessions()
                
                if machines:
                    last_active = time.time()
                else:
                    idle_time = time.time() - last_active
                    if idle_time > TIMEOUT_SECONDS:
                        logger.warning(f"Inactivity limit ({TIMEOUT_SECONDS}s) reached. Shutting down.")
                        os.kill(os.getpid(), signal.SIGTERM)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
