# ADR 0026: Ephemeral Worktrees and Isolation

## Status
Proposed

## Context
Users and autonomous agents need a way to perform experimental work (refactoring, feature exploration, automated patching) without polluting their primary working directory. We are implementing this using Git's native `worktree` feature to provide isolation while maintaining IDE compatibility.

### Constraints & Goals
1.  **Safety:** Experimental work must not corrupt the main repository.
2.  **Git-Centric:** This feature specifically targets Git-managed projects. The CLI will gracefully exit if run outside a Git worktree.
3.  **Statelessness:** The Gemini Hub remains stateless, using directory metadata for management.
4.  **IDE Integration:** Users must be able to open worktrees in their local IDE (e.g., VS Code).
5.  **Disk Management:** Automated cleanup for stale worktrees based on modification time.

## User Journeys

The worktree feature is designed to support the following high-level workflows:

1.  **The Fresh Start (New Feature):** A user wants to start work on a new branch in an isolated folder. The CLI handles branch creation (`git worktree add -b`) automatically.
    *   *Command:* `gemini-toolbox --worktree feat/ui-v2 chat`
2.  **The PR Repair (Existing Branch):** An agent (or human) needs to fix a bug in an existing branch. The CLI detects the branch and sets up the worktree correctly.
    *   *Command:* `gemini-toolbox --worktree fix/bug-123 chat`
3.  **The Autonomous Task (Non-Interactive):** An agent is launched with a specific instruction. It works in an ephemeral worktree to avoid locking the user's main working directory.
    *   *Command:* `gemini-toolbox --worktree "Refactor auth logic in app/models.py"`
4.  **The Parallel Multi-Tasker:** A user launches multiple agents on different branches simultaneously. Each lives in its own worktree.

## Proposed Decision: Smart Branching Logic

To ensure a seamless UX, the branching logic is **built into the `gemini-toolbox` wrapper**.

### Branch Resolution Protocol:
1.  **Explicit Branch Provided:** If the user provides a branch name (e.g., `--worktree feat/ui`), the CLI uses it directly.
2.  **Task Provided (Pre-Flight Naming):** If a task string is provided, a "Pre-Flight" call is made to a **Fast Model** (e.g., Gemini 2.5 Flash).
    *   **Constraint:** The model is invoked with a strict system instruction: "You are a git branch naming utility. Slugify the input task into a concise branch name. Return ONLY the slug. Do not analyze the codebase or provide explanations."
    *   The resulting slug is used for both the branch and the folder.
3.  **No Input Provided (Interactive Exploration):**
    *   The CLI creates a worktree with a **Detached HEAD** at the current commit.
    *   The folder is named `exploration-UUID`.
    *   **Benefit:** Allows the user to browse and experiment without creating a branch. The user can promote the state to a branch at any time using `git checkout -b` from within the worktree.

### Directory Structure:
To prevent clutter and allow for project-level management, worktrees are nested by project name:
`$XDG_CACHE_HOME/gemini-toolbox/worktrees/${PROJECT_NAME}/${SANITIZED_BRANCH_NAME}`

*   **Sanitization:** Slashes in branch names (e.g., `feat/ui`) are converted to hyphens (e.g., `feat-ui`) for the folder name to ensure filesystem compatibility and a flat structure within the project subfolder.

## Proposed Decision: Centralized Worktree Management

We will implement a centralized management strategy for ephemeral worktrees on the host disk:

*   **Location:** Defaults to the nested structure described above. This adheres to Linux standards for cached/transient data. Users can override this by setting `GEMINI_WORKTREE_ROOT`.
*   The Toolbox automatically mounts this path into the container.
*   **Cleanup:** The Hub will implement a "Stateless Reaper" protocol.
    *   **Mechanism:** Standard directory timestamp monitoring (`mtime`).
    *   The Hub periodically scans the project-level folders for directories with an `mtime` older than 30 days.
    *   Stale directories are removed, followed by `git worktree prune`.

## Non-Git Project Handling

If the `--worktree` flag is used in a directory that is not part of a Git repository, the `gemini-toolbox` script will:
1.  Detect the absence of a `.git` folder (via `git rev-parse`).
2.  Display a clear error message: `Error: --worktree can only be used within a Git repository.`
3.  Exit with a non-zero status code without launching the container or creating directories.

## Alternatives Considered

### 1. Project-Local Sandboxes (`.gemini/worktrees`)
*   **Idea:** Keep the worktrees inside a hidden folder within the project.
*   **Reason for Rejection:** Git worktrees cannot easily reside inside the parent worktree without recursion issues. It also pollutes the primary project directory, violating the "Zero Clutter" principle.

### 2. Relative Sibling Paths (`../project-sandbox`)
*   **Idea:** Create the worktree as a sibling directory.
*   **Reason for Rejection:** Highly fragile. The parent directory might be read-only, part of a different volume, or a disorganized "Downloads" folder. It creates "clutter sprawl" across the user's filesystem.

### 3. Pure Container Isolation (`--isolation container`)
*   **Idea:** Create the worktree inside a Docker Volume or a temporary path like `/tmp`, offering zero host footprint.
*   **Intended Use Case:** "The Risky Reviewer" - inspecting potentially malicious PRs without any files touching the host disk.
*   **Reason for Rejection:** 
    *   **IDE Friction:** Prevents host-based IDEs (VS Code) from accessing the files, breaking a core mandate of the toolbox.
    *   **Complexity:** Requires complex orchestration to manage volumes or temporary paths shared between containers.
    *   **Decision:** We prioritized developer experience (IDE access) over the extreme isolation required for malware analysis. If "Risky Review" becomes a critical need, we can revisit this as a specialized `gemini-toolbox --secure-review` mode in the future.

### 4. Filesystem-Level Snapshots (OverlayFS / Btrfs CoW)
*   **Idea:** Use Copy-on-Write snapshots or OverlayFS mounts.
*   **Reason for Rejection:** Significant overengineering. Requires specific filesystem support or elevated privileges (`sudo`). Native `git worktree` is idiomatic, portable, and natively understands branch logic.

## Trade-offs and Arbitrages

| Feature | Decision |
| :--- | :--- |
| **Visibility** | Visible to Host (VS Code) for high fidelity |
| **Cleanup** | Scheduled Reaper (mtime) for statelessness |
| **Speed** | Fast (Local FS) |
| **Context** | Git-Centric (Requires a repository) |

## Remaining Questions / Risks
*   **Orphaned Worktrees:** If a user deletes the main repository, the worktree entries in the root become "ghosts". The Reaper must be robust enough to handle directory removal even if the parent Git repo is missing.
*   **Branch Pollution:** Should automated tasks always use `detached HEAD` unless a branch name is explicitly provided?
