import time
import os
import signal
import logging
import threading
from app.config import Config
from app.services.tailscale import TailscaleService

logger = logging.getLogger(__name__)

class MonitorService:
    """Background service to monitor activity and auto-shutdown."""

    @staticmethod
    def start():
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
            time.sleep(10)
            try:
                # Check for peers
                status = TailscaleService.get_status()
                machines = TailscaleService.parse_peers(status)
                
                if machines:
                    last_active = time.time()
                else:
                    idle_time = time.time() - last_active
                    if idle_time > TIMEOUT_SECONDS:
                        logger.warning(f"Inactivity limit ({TIMEOUT_SECONDS}s) reached. Shutting down.")
                        os.kill(os.getpid(), signal.SIGTERM)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
