# ADR 0026: Ephemeral Worktrees and Sandbox Isolation

## Status
Proposed

## Context
Users and autonomous agents need a way to perform experimental work (refactoring, feature exploration, automated patching) without polluting their primary working directory. The previous attempt (referenced in `tmp/0023-ephemeral-worktrees-and-sandbox-root.md`) was partially implemented but reverted due to scope creep. We are reviving this with a focus on long-term maintainability and clear isolation strategies.

### Constraints & Goals
1.  **Safety:** Experimental work must not corrupt the main repository.
2.  **Git-Centric:** This feature specifically targets Git-managed projects. Non-git projects are out of scope.
3.  **Statelessness:** The Gemini Hub must remain stateless. We will not use a database to track sandboxes.
4.  **IDE Integration:** Humans need to be able to open sandboxes in their local IDE (e.g., VS Code).
5.  **Disk Management:** While the user is responsible for disk space, the system should provide automated cleanup mechanisms for stale sandboxes.

## Alternatives Considered

### 1. Host-Path Worktrees (`--isolation=disk`)
*   **Mechanism:** Create a `git worktree` in a centralized root folder (e.g., `~/gemini-sandboxes`).
*   **Pros:** Easy access from host (VS Code, terminal, GUI clients).
*   **Cons:** Leaves artifacts on the host disk that require active cleanup.

### 2. Volume-Based Worktrees (`--isolation=container`)
*   **Mechanism:** Create a `git worktree` inside a Docker Volume or the container's internal filesystem.
*   **Pros:** Truly ephemeral. No host disk clutter. Perfect for autonomous bots.
*   **Cons:** "Black Box" behavior. Local IDEs cannot easily access the files.

### 3. OverlayFS / Copy-on-Write
*   **Mechanism:** Use filesystem snapshots (Btrfs/ZFS) or OverlayFS mounts.
*   **Decision:** Rejected as overengineering. Stick to standard Git tooling for maximum compatibility.

## User Journeys

The sandbox feature is designed to support the following high-level workflows:

1.  **The Fresh Start (New Feature):** A user wants to start work on a new branch in an isolated folder. The CLI handles branch creation (`git worktree add -b`) automatically.
2.  **The PR Repair (Existing Branch):** An agent (or human) needs to fix a bug in an existing branch. The CLI detects the branch and sets up the worktree correctly.
3.  **The Autonomous Bot (Task Isolation):** A bot is launched with a specific instruction. It works in a sandbox to avoid locking the user's main working directory or polluting it with build artifacts.
4.  **The Parallel Multi-Tasker:** A user launches multiple agents on different branches simultaneously. Each lives in its own worktree, avoiding `index.lock` conflicts.
5.  **The Risky Reviewer:** A user wants to inspect a PR with potential side effects. Using `--isolation container` ensures the code remains entirely within Docker.

## Proposed Decision: Smart Branching Logic

To ensure a seamless UX, the branching logic is **built into the `gemini-toolbox` wrapper**. The agent inside the container does not need to handle Git plumbing to start working.

### Branch Resolution Protocol:
1.  **Branch Provided + Exists:** `git worktree add [path] [branch]`
2.  **Branch Provided + New:** `git worktree add -b [branch] [path]`
3.  **No Branch Provided:**
    *   Generates a UUID-based branch name (e.g., `gem-sandbox-a1b2`).
    *   Uses a `detached HEAD` if the intent is purely experimental.

## Proposed Decision: Dual-Mode Isolation

We will implement a unified `--sandbox` (or `--isolation`) flag that supports two distinct modes:

### 1. `disk` Mode (Default for Interactive Sessions)
Designed for human developers.
*   **Location:** Defaults to `$XDG_CACHE_HOME/gemini-toolbox/worktrees/${PROJECT_NAME}/${BRANCH_OR_UUID}`. This adheres to Linux standards for cached/transient data. Users can override this by setting `GEMINI_WORKTREE_ROOT`.
*   The Toolbox automatically mounts this path into the container.
*   **Cleanup:** The Hub will implement a "Stateless Reaper" protocol.
    *   **Mechanism:** Standard directory timestamp monitoring.
    *   The Hub periodically scans the root folder for directories with a modification time (`mtime`) older than 30 days.
    *   Stale directories are removed, followed by a `git worktree prune` to clean up metadata.

### 2. `container` Mode (Default for Autonomous/Bot Sessions)
Designed for ephemeral, automated tasks.
*   Worktrees are created within the container environment (using a dedicated volume).
*   Files vanish when the volume/container is destroyed.

## Trade-offs and Arbitrages

| Feature | `disk` Mode | `container` Mode |
| :--- | :--- | :--- |
| **Visibility** | Visible to Host (VS Code) | Hidden (Internal to Docker) |
| **Cleanup** | Manual or Scheduled Reaper | Automatic on Container/Vol exit |
| **Speed** | Fast (Local FS) | Variable (Volume Overhead) |
| **Risk** | Low (Centralized Root) | Zero (Isolated Vol) |

## Remaining Questions / Risks
*   **Orphaned Worktrees:** If a user deletes the main repository, the worktree entries in the sandbox root become "ghosts". The Reaper must be robust enough to handle directory removal even if the parent Git repo is missing.
*   **Branch Pollution:** Should sandboxes always use `detached HEAD` or generate UUID-based branch names to avoid cluttering the main repo's branch list?
