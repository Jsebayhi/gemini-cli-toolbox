import os
import time
import shutil
import logging
import threading
import subprocess
from app.config import Config

logger = logging.getLogger(__name__)

class PruneService:
    """Background service to clean up stale worktrees based on mtime."""

    @staticmethod
    def start():
        """Launch the background prune thread."""
        if not Config.HUB_WORKTREE_PRUNE_ENABLED:
            logger.info("Worktree Pruning disabled (explicitly toggled off).")
            return

        logger.info(f"Worktree Pruning started (Expiry: {Config.WORKTREE_EXPIRY_HEADLESS}d headless / {Config.WORKTREE_EXPIRY_BRANCH}d branch).")
        thread = threading.Thread(target=PruneService._prune_loop, daemon=True)
        thread.start()

    @staticmethod
    def _prune_loop():
        """Periodic cleanup loop."""
        # Run immediately on start, then every hour
        while True:
            try:
                PruneService.prune()
            except Exception as e:
                logger.error(f"Pruning error: {e}")
            
            time.sleep(3600)  # Sleep for 1 hour

    @staticmethod
    def prune():
        """Identify and remove stale worktree directories."""
        root = Config.WORKTREE_ROOT
        if not os.path.exists(root):
            logger.debug(f"Worktree root {root} does not exist. Skipping prune.")
            return

        now = time.time()
        pruned_count = 0
        
        # Structure: root/{project}/{worktree}
        try:
            for project_dir in os.listdir(root):
                project_path = os.path.join(root, project_dir)
                if not os.path.isdir(project_path):
                    continue
                    
                for worktree_dir in os.listdir(project_path):
                    worktree_path = os.path.join(project_path, worktree_dir)
                    if not os.path.isdir(worktree_path):
                        continue
                    
                    if PruneService.classify_and_prune(worktree_path, now):
                        pruned_count += 1
        except Exception as e:
            logger.error(f"Prune scan error: {e}")

        if pruned_count > 0:
            logger.info(f"Pruning finished. Removed {pruned_count} directories.")

    @staticmethod
    def classify_and_prune(worktree_path: str, now: float) -> bool:
        """Classifies a single worktree and prunes it if stale. Returns True if removed."""
        try:
            # Determine state using Git
            result = subprocess.run(
                ["git", "-C", worktree_path, "symbolic-ref", "-q", "HEAD"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                expiry_days = Config.WORKTREE_EXPIRY_BRANCH
                type_label = "branch"
            elif result.returncode == 1:
                expiry_days = Config.WORKTREE_EXPIRY_HEADLESS
                type_label = "headless"
            else:
                expiry_days = Config.WORKTREE_EXPIRY_ORPHAN
                type_label = "orphan"
        except Exception:
            expiry_days = Config.WORKTREE_EXPIRY_ORPHAN
            type_label = "error"

        # Check age
        try:
            mtime = os.path.getmtime(worktree_path)
            age_sec = now - mtime
            expiry_sec = expiry_days * 86400
            
            if age_sec > expiry_sec:
                logger.info(f"Pruning stale {type_label} worktree: {worktree_path} (Age: {int(age_sec/86400)} days)")
                shutil.rmtree(worktree_path)
                return True
        except Exception as e:
            logger.error(f"Failed to process/remove {worktree_path}: {e}")
            
        return False
