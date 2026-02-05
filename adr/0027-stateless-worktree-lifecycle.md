# ADR 0027: Stateless Lifecycle Management

## Status
Accepted

## Context
Ephemeral worktrees created in the cache directory (`$XDG_CACHE_HOME/gemini-toolbox/worktrees`) can accumulate over time, consuming significant disk space. We need a robust, low-maintenance way to clean up these workspaces without introducing a stateful database or a complex management layer that could fail or get out of sync.

### Constraints & Goals
1.  **Statelessness:** The Gemini Hub and Toolbox must remain stateless. We will not use an external database to track "active" worktrees.
2.  **Automation:** Cleanup should be passive. Users should not have to manually run "prune" commands to keep their system healthy.
3.  **Reliability:** We must avoid "false positives"—deleting a workspace that is still being used for an ongoing experiment.

## Decision: mtime-Based "Stateless Pruning"

We will implement a cleanup strategy based on standard Unix directory modification times (`mtime`).

### 1. The Pruning Policy (Differentiated Retention)
To balance between disk hygiene and long-term project context, we apply different retention periods based on the worktree's intent:

*   **Headless Worktrees (30 days):** Workspaces created without an explicit branch name (folder prefix `exploration-`) are considered transient and are pruned after 30 days of inactivity.
*   **Branch Worktrees (90 days):** Workspaces associated with a named branch are considered high-context and are preserved for 90 days.

*   **Configurability:** Both defaults can be overridden via environment variables:
    *   `GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS` (Default: 30)
    *   `GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS` (Default: 90)
*   **Explicit Control:** Automatic cleanup can be completely disabled using the `--no-worktree-prune` flag when starting the Gemini Hub, or by setting the `HUB_WORKTREE_PRUNE_ENABLED` environment variable to `false`.

### 2. Implementation Mechanism
The Gemini Hub periodically executes a "Pruning" routine (implemented via standard `find` logic):
1.  **Scan:** It recursively scans the project-level worktree folders.
2.  **Identify:** It identifies subdirectories with an `mtime` older than 30 days.
3.  **Remove:** It executes `rm -rf` on the stale directory.
4.  **Prune:** It follows up with a `git worktree prune` in the main repository (if reachable) to remove Git's internal metadata references to the deleted path.

### 3. Orphan & Error Handling
This stateless approach is uniquely resilient:
*   **Deleted Repos:** If a user deletes the main repository, the Pruner still finds and removes the cached worktree because it only relies on the worktree's own folder timestamp.
*   **Failed Tasks:** If an agent crashes and leaves a half-finished worktree, the Pruner will eventually clean it up.

## Alternatives Considered (Rejected)

### 1. SQLite/JSON Tracking Database
*   **Idea:** Maintain a list of all created worktrees and their status.
*   **Reason for Rejection:** Violates the "Stateless Hub" mandate. It introduces "Sync Drift"—the database might think a worktree exists when the user has already deleted it manually, or vice versa. The filesystem itself is the most accurate database of what actually exists.

### 2. Marker Files (`.gemini-touch`)
*   **Idea:** Every session `touch`es a specific hidden file to update the "last used" time.
*   **Reason for Rejection:** Unnecessary I/O. The directory's own `mtime` is automatically updated by the OS whenever files inside are changed, added, or removed. Relying on the OS timestamp is more efficient and "Unix-idiomatic."

### 3. Manual Cleanup Only (`gemini-toolbox prune`)
*   **Idea:** Provide a dedicated command for the user to clean their cache.
*   **Reason for Rejection:** High friction. Most users will forget to run it until they receive a "Disk Full" error. Automated background maintenance provides a better user experience.

## Trade-offs and Arbitrages

| Feature | Decision | Rationale |
| :--- | :--- | :--- |
| **State** | Stateless | Prevents data corruption and synchronization issues between the app and the disk. |
| **Reliability** | Unix `mtime` | Provides a built-in, kernel-level tracking mechanism for free. |
| **Precision** | 30-day window | Balances the risk of deleting "active" work with the need for disk hygiene. |
| **Orphanage** | Auto-handling | Ensures the cache doesn't leak if repositories are moved or deleted. |