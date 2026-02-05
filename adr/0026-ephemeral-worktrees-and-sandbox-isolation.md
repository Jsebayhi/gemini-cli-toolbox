# ADR 0026: Ephemeral Worktrees and Isolation

## Status
Accepted

## Context
Users and autonomous agents need a way to perform experimental work (refactoring, feature exploration, automated patching) without polluting their primary working directory. We are implementing this using Git's native `worktree` feature to provide isolation while maintaining IDE compatibility.

### Constraints & Goals
1.  **Safety:** Experimental work must not corrupt the main repository.
2.  **Git-Centric:** This feature specifically targets Git-managed projects. The CLI will gracefully exit if run outside a Git worktree.
3.  **Statelessness:** The Gemini Hub remains stateless, using directory metadata for management.
4.  **IDE Integration:** Users must be able to open worktrees in their local IDE (e.g., VS Code).
5.  **Disk Management:** Automated cleanup for stale worktrees based on modification time.

## User Journeys

The worktree feature supports the following high-level workflows:

1.  **The Fresh Start (New Feature):** A user wants to start work on a new branch. The CLI handles branch creation via AI naming based on the intent string.
    *   *Command:* `gemini-toolbox --worktree "Refactor auth logic"`
2.  **The PR Repair (Existing Branch):** A user needs to fix a bug in an existing branch. The CLI detects the branch and sets up the worktree correctly.
    *   *Command:* `gemini-toolbox --worktree fix/bug-123`
3.  **The Explicit Context:** A user wants to be 100% certain of the target branch, regardless of the prompt content.
    *   *Command:* `gemini-toolbox --worktree --branch feat/ui "Fix buttons"`
4.  **The Monitoring Session (Named Interaction):** A user wants an interactive session in a named workspace (e.g., to keep logs or context separate).
    *   *Command:* `gemini-toolbox --worktree "Monitor PR review comments"`
5.  **The Parallel Multi-Tasker:** A user launches multiple agents on different branches simultaneously. Each lives in its own worktree, avoiding `index.lock` conflicts.
6.  **The Risky Reviewer (Alternative Journey):** A user wants to inspect a PR with potential side effects. The worktree provides a layer of filesystem separation for these "look-but-don't-touch" scenarios.
7.  **Safe Exploration:** A user wants to browse the code or run a quick test without creating any branch or committing to a task.
    *   *Command:* `gemini-toolbox --worktree`

## Proposed Decision: Smart Resolution Architecture

We have decoupled the **Environment** (`--worktree`) from the **Context** (`--branch`) and the **Intent** (Positional Args).

### 1. The Priority Matrix
When `--worktree` is enabled, the Git reference is resolved using the following priority:

| Input Pattern | Logic Applied | Resulting Branch | Resulting Task |
| :--- | :--- | :--- | :--- |
| `--branch X ...` | **Explicit Override** | `X` | Remaining Args |
| `[Existing Branch] ...` | **Auto-Detection** | `[Existing Branch]` | Remaining Args |
| `[Task String] ...` | **AI Naming** | `ai-generated-slug` | `[Task String]` |
| (No arguments) | **Safe Default** | `Detached HEAD` | None |

### 2. The Syntactic Heuristic
To provide a "Just Works" experience without brittle keyword lists, the parser uses a **Non-Consuming Peek**:
*   The first positional argument is checked against the local Git references (`git show-ref`).
*   If a match is found, it is treated as the **Context** and removed from the agent's task list.
*   If no match is found (or if the arg contains spaces), the entire argument list is treated as the **Intent**, triggering a one-shot naming call to **Gemini 2.5 Flash**.

### 3. Pre-Flight AI Naming
When a task is provided without an explicit branch, the CLI performs a sub-second call to a "Fast" model (Gemini 2.5 Flash) with a strict system instruction:
*"You are a git branch naming utility. Slugify the input task into a concise branch name. Return ONLY the slug. Do not analyze the codebase or provide explanations."*

## Proposed Decision: Centralized Worktree Management

*   **Location:** Nested by project to prevent clutter: `$XDG_CACHE_HOME/gemini-toolbox/worktrees/${PROJECT_NAME}/${SANITIZED_BRANCH_NAME}`.
*   **Surgical Mount Strategy:** To protect the parent repository while allowing Git operations:
    *   The Parent Project is mounted as **Read-Only** (`:ro`).
    *   The Parent's `.git` directory is mounted as **Read-Write** (`:rw`) on top.
*   **Cleanup:** The Gemini Hub implements a "Stateless Reaper" that removes worktrees with an `mtime` older than 30 days.

## Alternatives Considered (Rejected)

### 1. Brittle Keyword Lists
*   **Idea:** Hardcode commands like `chat` or `hooks` to avoid consuming them as branches.
*   **Reason for Rejection:** High maintenance burden and fragile as the underlying CLI evolves.

### 2. Mandatory Terminator (`--`)
*   **Idea:** Force users to separate worktree args from agent args using `--`.
*   **Reason for Rejection:** Standard but poor UX. Users forget it, leading to "branch named 'chat'" bugs.

### 3. Pure Container Isolation (`--isolation container`)
*   **Idea:** Worktree inside a Docker Volume.
*   **Reason for Rejection:** Prevents VS Code/local IDE integration, breaking a core mandate of the toolbox.

### 4. Filesystem Snapshots (OverlayFS / CoW)
*   **Idea:** Use Btrfs/ZFS snapshots.
*   **Reason for Rejection:** Platform-specific (Linux only) and requires elevated privileges. Git Worktrees are standard and portable.

## Technical Constraints

*   **Non-Git Projects:** The feature requires a Git repository. The CLI checks for a `.git` folder (via `git rev-parse`) and exits gracefully with an error if used in a regular directory.
*   **Empty Repositories:** Worktree creation is forbidden if the repository has zero commits (no `HEAD`).
*   **Recursive Worktrees:** Creating a worktree from *within* an existing worktree is forbidden to keep logic simple and robust.