# ADR 0028: Worktree Reference Resolution

## Status
Accepted

## Context
When a user launches a session with `--worktree`, the tool needs a deterministic way to decide which Git reference (branch) to use and how to handle positional arguments. We want a robust, predictable experience that follows the principle of "What you type is what you get."

## Decision: Manual Resolution Hierarchy

We have implemented a priority-based resolution system that handles explicit flags, existing branches, and manual naming.

### 1. The Priority Matrix

| Input Pattern | Logic Applied | Resulting Branch | Resulting Task |
| :--- | :--- | :--- | :--- |
| `--name X ...` | **Explicit Override** | `X` | Remaining Args |
| `[Existing Branch] ...` | **Auto-Detection** | `[Existing Branch]` | Remaining Args |
| `[New Name] [Task]` | **Manual Naming** | `[New Name]` | `[Task]` |
| (No arguments) | **Safe Default** | `Detached HEAD` | None |

### 2. The Syntactic Heuristic (Non-Consuming Peek)
To avoid maintaining brittle keyword lists, the parser uses a "strongest signal" heuristic:
1.  **Peek:** The tool peeks at the first positional argument.
2.  **Verify:** It checks if this argument matches an existing local branch (via `git show-ref`).
3.  **Result:**
    *   **If Branch exists:** It is used as the context. Remaining arguments are passed to the agent.
    *   **If Branch does NOT exist:** The argument is used as the **New Branch/Folder Name**. Remaining arguments are passed as the Task.
    *   **Fallback:** If no arguments are provided, it defaults to a detached HEAD exploration (`exploration-UUID`).

### 3. Naming & Sanitization
*   **Philosophy:** Predictability over automation.
*   **Terminology:** We use the term **Name** to represent the 1:1 mapping between the worktree folder and the Git branch.
*   **Sanitization:** The tool replaces slashes (`/`) with dashes (`-`) for the filesystem folder name to ensure compatibility, but preserves the Git branch name exactly as provided by the user.

## User Journeys

*   **Explicit Context:** `gemini-toolbox --worktree --name feat/ui "Fix buttons"` -> Uses `feat/ui`.
*   **Manual Naming:** `gemini-toolbox --worktree fix-auth "Refactor login"` -> Creates `fix-auth` branch, passes task to agent.
*   **Resume Work:** `gemini-toolbox --worktree fix-auth` -> Detects `fix-auth` exists, enters it, and starts an interactive session.
*   **Multi-Session Collaboration:** `gemini-toolbox --worktree fix-auth` (in two different terminals) -> Both sessions share the same `fix-auth` worktree, allowing for concurrent agent/human collaboration in the same isolated environment.
*   **Safe Exploration:** `gemini-toolbox --worktree` -> Creates a detached HEAD worktree.

## Trade-offs and Arbitrages

| Aspect | Implementation | Rationale |
| :--- | :--- | :--- |
| **Logic** | Heuristic (Strongest Signal) | Balances ease-of-use with Git robustness. |
| **Naming** | Manual / Explicit | Removes dependencies on complex pre-flight containers. |
| **Safety** | Explicit `--name` always wins | Provides a guarantee for ambiguous cases. |
| **Reliability** | Deterministic | "What you type is what you get" avoids AI hallucinations. |

## Related Decisions
*   **ADR 0030**: Rejection of Automatic Task-Based Naming.
