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
    def _get_age_seconds(path: str) -> float:
        """Returns the age of a path in seconds."""
        try:
            mtime = os.path.getmtime(path)
            return time.time() - mtime
        except Exception:
            return 0

    @staticmethod
    def _get_worktree_info(path: str) -> tuple[int, str]:
        """Returns (expiry_seconds, type_label) for a worktree."""
        try:
            result = subprocess.run(
                ["git", "-C", path, "symbolic-ref", "-q", "HEAD"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                return Config.WORKTREE_EXPIRY_BRANCH * 86400, "branch"
            elif result.returncode == 1:
                return Config.WORKTREE_EXPIRY_HEADLESS * 86400, "headless"
            else:
                return Config.WORKTREE_EXPIRY_ORPHAN * 86400, "ambiguous/orphan"
        except Exception:
            return Config.WORKTREE_EXPIRY_ORPHAN * 86400, "error/fallback"

    @staticmethod
    def prune():
        """Identify and remove stale worktree directories."""
        root = Config.WORKTREE_ROOT
        if not os.path.exists(root):
            logger.debug(f"Worktree root {root} does not exist. Skipping prune.")
            return

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
                
                expiry_seconds, type_label = PruneService._get_worktree_info(worktree_path)
                age = PruneService._get_age_seconds(worktree_path)
                
                if age > expiry_seconds:
                    logger.info(f"Pruning stale {type_label} worktree: {worktree_path} (Age: {int(age/86400)} days)")
                    try:
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
