# ADR 0029: Worktree Retention & Orphan Policy

## Status
Accepted

## Context
The Gemini Hub is responsible for cleaning up stale worktrees to manage disk usage. However, because the Hub runs in a container with a restricted view of the host filesystem, it often cannot execute `git` commands to introspect the worktree state (e.g., checking if it's on a branch or detached HEAD) due to absolute path mismatches in the `.git` file.

### The "Orphan by Viewpoint" Problem
A Git Worktree contains a `.git` file pointing to the absolute path of the parent repository (e.g., `/home/user/project/.git`). Inside the Hub container, this path likely does not exist. Therefore, the Hub cannot reliably distinguish between a "Headless" worktree and a "Branch" worktree using standard Git tools.

## Decision: Path-Based Contract with Safety Defaults

We will rely on a strict folder naming convention established by the Toolbox at creation time, coupled with a "Safety First" default for ambiguous cases.

### 1. The Path-Based Contract
The `gemini-toolbox` enforces the following naming schema:
*   **Transient Worktrees:** Must start with the prefix `exploration-` (e.g., `exploration-a1b2c3d4`).
*   **Persistent Worktrees:** Must use the branch slug (e.g., `feature-login-fix`).

### 2. The Retention Matrix
The Pruner applies retention policies based purely on the folder name:

| Folder Name Pattern | Classification | Retention Period | Config Variable |
| :--- | :--- | :--- | :--- |
| `exploration-*` | **Transient** | 30 Days | `GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS` |
| `*` (Everything else) | **Persistent** | 90 Days | `GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS` |

### 3. Orphan Safety Policy
If a worktree is "Orphaned" (parent repo deleted) or its state is otherwise ambiguous to the system, we implicitly treat it as **Persistent** (falling into the `*` bucket).
*   **Rationale:** Prematurely deleting user data is a critical failure. Wasting disk space for an additional 60 days is an acceptable trade-off to ensure no work is lost due to misclassification.

## Alternatives Considered

### 1. Git Introspection (`git symbolic-ref`)
*   **Idea:** Run `git` commands inside the worktree to check HEAD state.
*   **Reason for Rejection:** Fails inside the container due to the "Orphan by Viewpoint" path mismatch described above.

### 2. Marker Files (`.gemini-type`)
*   **Idea:** Drop a file indicating the type at creation.
*   **Reason for Rejection:** Adds I/O and complexity. It also becomes stale if a user manually promotes a detached worktree to a branch (e.g., `git checkout -b`) without the tool updating the marker. The Folder Name is a more immutable signal of *original intent*.

## Trade-offs and Arbitrages

| Feature | Decision |
| :--- | :--- |
| **Precision** | Medium (Relies on naming convention) |
| **Safety** | High (Defaults to Max Retention) |
| **Robustness** | High (Works across container boundaries) |
