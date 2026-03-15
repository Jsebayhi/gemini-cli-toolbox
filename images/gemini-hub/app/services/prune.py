import os
import time
import shutil
import logging
import threading
import subprocess
from app.config import Config

logger = logging.getLogger(__name__)

class PruneService:
    """Background service to clean up stale worktrees and orphaned sidecars."""

    @staticmethod
    def start():
        """Launch the background prune thread."""
        if not Config.HUB_WORKTREE_PRUNE_ENABLED:
            logger.info("Pruning disabled (explicitly toggled off).")
            return

        logger.info(f"Pruning started (Expiry: {Config.WORKTREE_EXPIRY_HEADLESS}d headless / {Config.WORKTREE_EXPIRY_BRANCH}d branch).")
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
        """Main entry point for all pruning tasks."""
        PruneService._prune_worktrees()
        PruneService._prune_sidecars()

    @staticmethod
    def _prune_worktrees():
        """Identify and remove stale worktree directories."""
        root = Config.WORKTREE_ROOT
        if not os.path.exists(root):
            logger.debug(f"Worktree root {root} does not exist. Skipping prune.")
            return

        expiry_headless_sec = Config.WORKTREE_EXPIRY_HEADLESS * 86400
        expiry_branch_sec = Config.WORKTREE_EXPIRY_BRANCH * 86400
        expiry_orphan_sec = Config.WORKTREE_EXPIRY_ORPHAN * 86400
        
        now = time.time()
        
        try:
            # First level: Project directories
            for project in os.listdir(root):
                project_path = os.path.join(root, project)
                if not os.path.isdir(project_path):
                    continue
                
                # Second level: Worktree directories
                for wt in os.listdir(project_path):
                    wt_path = os.path.join(project_path, wt)
                    if not os.path.isdir(wt_path):
                        continue
                    
                    # Classification via git
                    category = "orphan"
                    try:
                        res = subprocess.run(
                            ["git", "-C", wt_path, "symbolic-ref", "HEAD"],
                            capture_output=True, text=True, timeout=5
                        )
                        if res.returncode == 0:
                            category = "branch"
                        elif res.returncode == 1:
                            category = "headless"
                    except Exception:
                        pass
                    
                    # Age check
                    mtime = os.path.getmtime(wt_path)
                    age = now - mtime
                    
                    threshold = expiry_orphan_sec
                    if category == "headless":
                        threshold = expiry_headless_sec
                    elif category == "branch":
                        threshold = expiry_branch_sec
                    
                    if age > threshold:
                        logger.info(f"Pruning stale {category} worktree: {wt_path} (Age: {int(age/86400)}d)")
                        try:
                            shutil.rmtree(wt_path)
                        except Exception as e:
                            logger.error(f"Failed to remove {wt_path}: {e}")
        except Exception as e:
            logger.error(f"Error during worktree prune: {e}")

    @staticmethod
    def _prune_sidecars():
        """Identify and remove orphaned -vpn containers."""
        try:
            # 1. Find all containers with -vpn suffix
            cmd = ["docker", "ps", "-a", "--format", "{{.Names}}", "--filter", "name=-vpn"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return

            sidecars = result.stdout.splitlines()
            for sidecar in sidecars:
                # 2. Extract parent ID
                parent_id = sidecar.replace("-vpn", "")
                
                # 3. Check if parent is running
                check_cmd = ["docker", "inspect", "-f", "{{.State.Running}}", parent_id]
                check_res = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
                
                # If parent doesn't exist or isn't running, kill the sidecar
                if check_res.returncode != 0 or check_res.stdout.strip() != "true":
                    logger.info(f"Pruning orphaned sidecar: {sidecar} (Parent {parent_id} is gone)")
                    subprocess.run(["docker", "stop", sidecar], capture_output=True, timeout=10)
        except Exception as e:
            logger.error(f"Error during sidecar prune: {e}")
