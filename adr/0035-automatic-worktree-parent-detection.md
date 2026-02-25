# ADR-0035: Automatic Worktree Parent Detection

## Status
Accepted

## Context
The Gemini Toolbox uses Git Worktrees for task isolation (ADR-0026). These worktrees reside in a centralized cache and depend on the parent repository for their object database and history. 

Currently, the "Surgical Mount" strategy (mounting the parent RO and `.git` RW) is only applied when `gemini-toolbox` is used to *create* a worktree via the `--worktree` flag. When a session is resumed from an existing worktree (e.g., via Gemini Hub discovery), the toolbox treats the directory as a standard standalone project. This breaks Git functionality inside the container because the worktree's internal `.git` file points to a host path that is not mounted.

## Decision
We will modify `bin/gemini-toolbox` to automatically detect if the target `PROJECT_DIR` is a Git worktree during the initialization phase, regardless of whether the `--worktree` flag was used.

### Detection Mechanism
The script will perform the following checks:
1.  Verify the path is inside a Git repository: `git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree`.
2.  Determine if it is a worktree (vs a main repo): Check if `.git` at the repo toplevel is a file.
3.  Resolve the parent repository root: `git -C "$PROJECT_DIR" rev-parse --git-common-dir`.

### Mount Strategy
If a parent is detected, the script will automatically apply the Surgical Mount strategy defined in ADR-0026:
- **Parent Root:** Mounted as Read-Only (`:ro`).
- **Parent .git:** Mounted as Read-Write (`:rw`).

## Alternatives Considered (Rejected)

### 1. Explicit Hub Logic
*   **Idea:** Modify Gemini Hub to detect worktrees and pass parent mount arguments (e.g., `--docker-args`) to the toolbox.
*   **Reason for Rejection:** This violates the "Stateless Hub" principle and adds significant complexity to the Hub's Python backend. It also doesn't solve the problem for users manually launching sessions from the worktree cache via the CLI.

### 2. Path-Based Inference
*   **Idea:** Infer the parent repository path based on the standard worktree cache structure (e.g., `worktrees/{project-name}`).
*   **Reason for Rejection:** Highly fragile. Users can override the worktree root via `GEMINI_WORKTREE_ROOT`, or manually move worktree folders. Relying on path conventions is less robust than using Git's own metadata for discovery.

### 3. Full Clones for Isolation
*   **Idea:** Use full clones instead of worktrees for task isolation.
*   **Reason for Rejection:** Already rejected in ADR-0026. Full clones are slow, consume significant disk space, and lack the lightweight "shared object database" benefits of worktrees.

## Consequences
- **Robustness:** Resuming sessions from the Hub or manual CLI calls in worktree folders will have full Git support.
- **Statelessness:** The Hub does not need to store metadata about worktree parentage; it is discovered dynamically by the toolbox wrapper.
- **Security:** Maintains the existing security model where the parent repository is protected from accidental modifications.
- **Overhead:** Adds a negligible startup delay (a few milliseconds) for the `git` metadata check.
