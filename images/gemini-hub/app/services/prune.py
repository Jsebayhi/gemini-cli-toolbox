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
        # Safety Limit: Maximum of any configured retention
        expiry_safety_sec = max(expiry_headless_sec, expiry_branch_sec)
        
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
                
                # Determine state using Git
                # Branch: returns 0, Headless: returns 1, Orphan/Error: returns other
                try:
                    result = subprocess.run(
                        ["git", "-C", worktree_path, "symbolic-ref", "-q", "HEAD"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        expiry_seconds = expiry_branch_sec
                        type_label = "branch"
                    elif result.returncode == 1:
                        expiry_seconds = expiry_headless_sec
                        type_label = "headless"
                    else:
                        # Safety Default: Max retention for orphans/errors
                        expiry_seconds = expiry_safety_sec
                        type_label = "ambiguous/orphan"
                except Exception:
                    expiry_seconds = expiry_safety_sec
                    type_label = "error/fallback"
                
                # Check directory mtime
                mtime = os.path.getmtime(worktree_path)
                age = now - mtime
                
                if age > expiry_seconds:
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
