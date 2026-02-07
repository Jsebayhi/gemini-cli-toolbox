# ADR 0028: Worktree Reference Resolution

## Status
Accepted

## Context
When a user launches a session with `--worktree`, the tool needs a deterministic way to decide which Git reference (branch) to use and how to handle positional arguments. We want a robust, predictable experience that eliminates ambiguity and follows the principle of "Explicit over Implicit."

## Decision: Explicit Resolution Policy

We have implemented a binary resolution system that handles only two states: Explicitly Named and Anonymous.

### 1. The Priority Matrix

| Input Pattern | Resolution Logic | Resulting Context | Resulting Task |
| :--- | :--- | :--- | :--- |
| `--name MY-ID ...` | **Explicit Naming** | Branch & Folder: **`MY-ID`** | All positional args |
| (No arguments) | **Anonymous Exploration** | Branch: **`Detached HEAD`** <br> Folder: **`exploration-UUID`** | None |
| `[Prompt String]` | **Anonymous Task** | Branch: **`Detached HEAD`** <br> Folder: **`exploration-UUID`** | All positional args |

### 2. Elimination of Positional Detection
To ensure 100% reliability and avoid "The Branch named 'Fix'" bug, we have **REJECTED** the use of positional arguments for identifying branches.
*   The first positional argument is **never** used as a branch name.
*   The only way to create or target a named worktree is via the explicit `--name` flag.
*   This ensures that any prompt passed to the agent (e.g., `gemini-toolbox --worktree "Refactor the auth"`) is correctly handled as a task, not as an attempt to create a branch named `Refactor`.

### 3. Naming & Sanitization
*   **Philosophy:** Predictability over automation.
*   **Terminology:** We use the term **Name** to represent the 1:1 mapping between the worktree folder and the Git branch.
*   **Sanitization:** The tool replaces slashes (`/`) with dashes (`-`) for the filesystem folder name to ensure compatibility, but preserves the Git branch name exactly as provided by the user.

## User Journeys

*   **Explicit Context:** `gemini-toolbox --worktree --name feat/ui "Fix buttons"` -> Creates/Uses `feat/ui` branch and folder.
*   **Safe Exploration (with task):** `gemini-toolbox --worktree "Refactor login"` -> Creates an anonymous `exploration-UUID` folder with a detached HEAD and passes the task to the agent.
*   **Multi-Session Collaboration:** `gemini-toolbox --worktree --name fix-auth` (in two terminals) -> Both sessions share the same `fix-auth` worktree.
*   **Blind Exploration:** `gemini-toolbox --worktree` -> Creates an anonymous detached HEAD worktree with no task.

## Trade-offs and Arbitrages

| Aspect | Implementation | Rationale |
| :--- | :--- | :--- |
| **Logic** | Binary (Explicit vs Anon) | Maximizes reliability by removing all heuristics. |
| **Naming** | Manual Only | Eliminates fragile dependencies on AI or keyword peeking. |
| **Safety** | Detached by Default | Prevents accidental branch creation when users provide tasks. |
| **Reliability** | Deterministic | "Explicit is better than implicit." |

## Related Decisions
*   **ADR 0030**: Rejection of Automatic Task-Based Naming.