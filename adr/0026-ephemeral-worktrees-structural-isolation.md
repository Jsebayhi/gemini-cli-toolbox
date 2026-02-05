# ADR 0026: Ephemeral Worktrees and Structural Isolation

## Status
Accepted

## Context
Users and autonomous agents need a way to perform experimental work (refactoring, feature exploration, automated patching) without polluting their primary working directory. The desired capability is "Ephemeral Workspaces" where the agent can work in high-fidelity isolation while maintaining full compatibility with host-based tools like VS Code.

### Constraints & Goals
1.  **Safety:** Experimental work must not corrupt the main repository or lead to accidental modification of the primary codebase.
2.  **Git-Centric:** This feature specifically targets Git-managed projects. The CLI must gracefully handle non-Git environments.
3.  **Zero Clutter:** Creating copies of the project should not clutter the user's primary workspace (e.g., no `../project-copy` sprawl).
4.  **IDE Integration:** Users must be able to open worktrees in their local IDE (e.g., VS Code) with full feature support (IntelliSense, Debugging).
5.  **Performance:** Context switching should be near-instant and avoid the overhead of full clones.

## Decision: Native Git Worktrees

We will use Git's native `worktree` feature as the primary isolation primitive. Unlike a full clone, a worktree shares the same object database as the parent repository, making it extremely lightweight and fast to create.

### 1. Centralized, Project-Nested Cache
To prevent "directory sprawl," all worktrees are stored in a centralized cache:
`$XDG_CACHE_HOME/gemini-toolbox/worktrees/${PROJECT_NAME}/${SANITIZED_BRANCH_NAME}`

*   **Standard Compliance:** Using `$XDG_CACHE_HOME` (defaulting to `~/.cache`) adheres to Linux standards for transient data that can be safely deleted if disk space is needed.
*   **Organization:** Grouping by `${PROJECT_NAME}` allows users to easily manage or audit all isolated workspaces belonging to a specific repository.
*   **Sanitization logic:** To ensure filesystem compatibility and a flat structure within the project subfolder, slashes in branch names (e.g., `feat/ui`) are automatically converted to hyphens (e.g., `feat-ui`) for the folder name.

### 2. Surgical Mount Strategy (Security & Robustness)
To enable full Git functionality inside the container while protecting the user's main repository, the toolbox implements a dual-mount approach:
1.  **Worktree Root:** Mounted as the primary workspace (`Read-Write`).
2.  **Parent Project:** Mounted as **Read-Only** (`:ro`). This allows the agent to read scripts, configurations, or Git hooks located in the parent repo without any risk of modifying the primary source code.
3.  **Parent's `.git` Directory:** Mounted as **Read-Write** (`:rw`) on top of the parent mount. This is required for Git to write new commits, update branch references, and manage the shared object database.

## Technical Constraints & Safety

*   **Non-Git Projects:** The tool checks for a `.git` folder (via `git rev-parse`) and exits gracefully with a clear error message if run in a regular directory.
*   **Empty Repositories:** Worktree creation is forbidden if the repository has zero commits (no `HEAD`), as Git requires a valid reference to branch from.
*   **Nested Worktrees (No Recursion):** Creating a worktree from *within* another worktree is explicitly forbidden. This avoids complex recursive metadata resolution and ensures the surgical mount strategy remains predictable and secure.

## Alternatives Considered (Rejected)

### 1. Project-Local Sandboxes (`.gemini/worktrees`)
*   **Idea:** Keep the worktrees inside a hidden folder within the project.
*   **Reason for Rejection:** Git worktrees cannot easily reside inside the parent worktree without recursion issues and significant `.gitignore` complexity. It also pollutes the primary project directory, violating our "Zero Clutter" principle.

### 2. Relative Sibling Paths (`../project-sandbox`)
*   **Idea:** Create the worktree as a sibling directory to the project.
*   **Reason for Rejection:** Highly fragile. The parent directory might be read-only, part of a different volume, or a disorganized "Downloads" folder. It creates "clutter sprawl" across the user's filesystem that is hard to track and clean.

### 3. Pure Container Isolation (`--isolation container`)
*   **Idea:** Create the worktree inside a Docker Volume or the container's internal filesystem (or a temporary path like `/tmp`).
*   **Pros:** Theoretically "zero footprint" on the host disk's primary partitions.
*   **Cons:** 
    *   **IDE Friction:** Prevents the host's VS Code from accessing the files, breaking one of the core mandates of the toolbox.
    *   **Complexity:** Requires complex orchestration to manage volumes or temporary paths shared between containers.
    *   **Redundancy:** The `disk` mode using `$XDG_CACHE_HOME` already provides sufficient isolation from the user's primary workspace.
*   **Decision:** **REJECTED.** The marginal benefit of "container-only" storage does not outweigh the loss of developer productivity (IDE access) and the maintenance burden of a dual-path implementation. We chose to keep the tool simple and stick to the single, robust disk-based variant.

### 4. Filesystem-Level Snapshots (OverlayFS / Btrfs CoW)
*   **Idea:** Use Copy-on-Write snapshots or OverlayFS mounts.
*   **Reason for Rejection:** Significant overengineering. Requires specific filesystem support (Btrfs/ZFS) or elevated privileges (`sudo`). Native `git worktree` is standard, portable, and natively understands branch logic.

## Trade-offs and Arbitrages

| Feature | Decision | Rationale |
| :--- | :--- | :--- |
| **Visibility** | Visible to Host (VS Code) | Essential for developer productivity and debugging. |
| **Speed** | Fast (Local FS) | Worktrees avoid the time/space overhead of full clones. |
| **Context** | Git-Centric | We chose to rely on standard Git tooling rather than building a custom shadowing system. |
| **Safety** | Surgical Mounts | Provides RO protection for parent files while allowing Git persistence. |