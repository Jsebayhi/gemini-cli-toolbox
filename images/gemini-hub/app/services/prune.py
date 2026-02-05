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

        expiry_headless_sec = Config.WORKTREE_EXPIRY_HEADLESS * 86400
        expiry_branch_sec = Config.WORKTREE_EXPIRY_BRANCH * 86400
        now = time.time()
        
        pruned_count = 0
        
        # Structure: root/{project}/{worktree}
        for project_dir in os.listdir(root):
            project_path = os.path.join(root, project_dir)
            if not os.path.isdir(project_path):
                continue
                
            for worktree_dir in os.listdir(project_path):
                worktree_path = os.path.join(project_path, worktree_dir)
                if not os.path.isdir(worktree_path):
                    continue
                
                # Determine expiry based on folder prefix
                is_headless = worktree_dir.startswith("exploration-")
                expiry_seconds = expiry_headless_sec if is_headless else expiry_branch_sec
                
                # Check directory mtime
                mtime = os.path.getmtime(worktree_path)
                age = now - mtime
                
                if age > expiry_seconds:
                    type_label = "headless" if is_headless else "branch"
                    logger.info(f"Pruning stale {type_label} worktree: {worktree_path} (Age: {int(age/86400)} days)")
                    try:
                        # Recursive removal of the directory
                        shutil.rmtree(worktree_path)
                        pruned_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {worktree_path}: {e}")

        if pruned_count > 0:
            logger.info(f"Pruning finished. Removed {pruned_count} directories.")
            # Final global prune call to clean up Git metadata
            # This requires access to a git repo. We can't easily guarantee which one.
            # But the Hub often runs gemini-toolbox which can be used or just 'git'.
            # We'll skip the explicit 'git worktree prune' for now as Git handles it
            # when the user next runs a command in the main repo.
