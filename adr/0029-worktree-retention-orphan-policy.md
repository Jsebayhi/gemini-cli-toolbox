# ADR 0029: Worktree Retention & Orphan Policy

## Status
Accepted

## Context
The Gemini Hub is responsible for cleaning up stale worktrees to manage disk usage. However, because the Hub runs in a container with a restricted view of the host filesystem, it often cannot execute `git` commands to introspect the worktree state (e.g., checking if it's on a branch or detached HEAD) due to absolute path mismatches in the `.git` file.

### The "Orphan by Viewpoint" Problem
A Git Worktree contains a `.git` file pointing to the absolute path of the parent repository (e.g., `/home/user/project/.git`). Inside the Hub container, this path likely does not exist. Therefore, the Hub cannot reliably distinguish between a "Headless" worktree and a "Branch" worktree using standard Git tools.

## Decision: Git-Based Introspection with Safety Defaults

We will rely on actual Git state to determine retention policies, while applying a "Safety First" default for cases where introspection is impossible.

### 1. Retention Tiers
The Pruner classifies worktrees into three tiers based on their Git `HEAD` state:

| Git State | Classification | Retention Period | Config Variable |
| :--- | :--- | :--- | :--- |
| **Branch** (`symbolic-ref` success) | **Persistent** | 90 Days | `GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS` |
| **Headless** (`symbolic-ref` failure) | **Transient** | 30 Days | `GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS` |
| **Orphan/Error** (Cmd fails) | **Ambiguous (Safety)**| 90 Days | `GEMINI_WORKTREE_ORPHAN_EXPIRY_DAYS` |

### 2. Implementation Mechanism
The Hub runs `git -C <path> symbolic-ref -q HEAD` for each candidate directory:
*   **Exit 0:** Confirms a branch reference exists.
*   **Exit 1:** Confirms a detached HEAD state.
*   **Other/Error:** Indicates an orphaned worktree or a path resolution error (common in containerized environments).

### 3. Orphan Safety Policy
If a worktree's state is ambiguous (e.g., the parent repo path in the `.git` file cannot be resolved from within the Hub container), the system **defaults to the dedicated Orphan Retention period**.
*   **Rationale:** Data preservation is prioritized over disk optimization. By using a dedicated safety threshold (defaulting to 90 days), we ensure that potentially active work is not lost due to container-level path visibility issues.

## Alternatives Considered

### 1. Folder Naming Convention (Path-Based Contract)
*   **Idea:** Prefix detached worktrees with `exploration-`.
*   **Reason for Rejection:** While used by the Toolbox for organization, it is a weak signal for lifecycle management. Actual Git state is the only 100% accurate "Ground Truth."

### 2. Marker Files (`.gemini-type`)
*   **Idea:** Drop a file indicating the type at creation.
*   **Reason for Rejection:** Adds I/O and complexity. It also becomes stale if a user manually promotes a detached worktree to a branch (e.g., `git checkout -b`) without the tool updating the marker. The Folder Name is a more immutable signal of *original intent*.

## Trade-offs and Arbitrages

| Aspect | Implementation |
| :--- | :--- |
| **Classification Accuracy** | **High** for visible repositories (Git-based); **Conservative Fallback** for orphans. |
| **Data Safety** | **Maximal** (Ambiguous worktrees default to the dedicated safety limit). |
| **Environmental Resilience** | **High** (Works reliably across container boundaries and path mismatches). |


