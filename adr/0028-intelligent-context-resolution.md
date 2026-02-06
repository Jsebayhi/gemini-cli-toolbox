# ADR 0028: Intelligent Context Resolution

## Status
Accepted

## Context
When a user launches a session with `--worktree`, the tool needs to decide which Git reference (branch) to use and what task the agent should perform. We want a "Just Works" experience that minimizes manual typing while avoiding the maintenance burden of brittle keyword lists.

### Constraints & Goals
1.  **Semantic Clarity:** Use AI to name branches when the user provides a task description.
2.  **Orthogonality:** Decouple the **Environment** (`--worktree`) from the **Context** (`--branch`) and the **Intent** (Task positional args).
3.  **Ambiguity Resolution:** Handle cases where a single string could be a branch name OR a prompt (e.g., `gemini-toolbox --worktree chat`).

## Decision: Smart Resolution Priority

We have implemented a deterministic resolution hierarchy that combines explicit flags and manual naming.

### 1. The Priority Matrix
When `--worktree` is enabled, the Git reference is resolved using the following priority:

| Input Pattern | Logic Applied | Resulting Branch | Resulting Task |
| :--- | :--- | :--- | :--- |
| `--branch X ...` | **Explicit Override** | `X` | Remaining Args |
| `[Existing Branch] ...` | **Auto-Detection** | `[Existing Branch]` | Remaining Args |
| `[New Name] [Task]` | **Manual Naming** | `[New Name]` | `[Task]` |
| (No arguments) | **Safe Default** | `Detached HEAD` | None |

### 2. The Syntactic Heuristic (Non-Consuming Peek)
To avoid brittle keyword lists (which require constant updates as the CLI subcommands grow), the parser uses a "strongest signal" heuristic:
1.  **Peek:** The tool peeks at the first positional argument.
2.  **Verify:** It checks if this argument matches an existing local branch (via `git show-ref`).
3.  **Result:**
    *   **If Branch exists:** It is consumed as the **Context**. The remaining arguments are passed to the agent.
    *   **If Branch does NOT exist:** The argument is treated as the **New Branch Name**. The remaining arguments are treated as the Task.
    *   **Fallback:** If no arguments are provided, it defaults to a detached HEAD exploration.

### 3. Manual Naming & Fallback
We explicitly **REJECT** automatic AI-based branch naming (see Alternatives Considered).
*   **Philosophy:** "What you type is what you get."
*   **Mechanism:** If the user provides `gemini-toolbox --worktree fix-bug`, we create a branch named `fix-bug`.
*   **Sanitization:** The tool sanitizes the input string (replacing slashes with dashes for the folder name) but preserves the branch name as-is.

## User Journeys

*   **The Fresh Start:** `gemini-toolbox --worktree feature/auth "Refactor login"` -> Creates `feature/auth` branch, passes "Refactor login" to agent.
*   **The PR Repair (Resumable):** `gemini-toolbox --worktree fix/bug-123 chat` -> Tool detects branch, sets up worktree, and starts interactive chat.
*   **The Explicit Context:** `gemini-toolbox --worktree --branch feat/ui "Fix buttons"` -> Guaranteed to use `feat/ui`.
*   **Safe Exploration:** `gemini-toolbox --worktree` (No args) -> Creates a detached HEAD worktree.

## Alternatives Considered (Rejected)

### 1. Automatic AI Branch Naming
*   **Idea:** Pass the task description to a Gemini Flash model to generate a slug (e.g., "Refactor the auth" -> `refactor-auth`).
*   **Reason for Rejection:**
    *   **Fragility:** Requires a complex "Pre-Flight" container with full environment propagation (Auth, Network, Proxies).
    *   **Unpredictability:** Users found it confusing when the generated name didn't match their mental model.
    *   **Security:** Requires mounting the project (Read-Only) to provide context, which increases the attack surface.

## Trade-offs and Arbitrages

| Feature | Decision | Rationale |
| :--- | :--- | :--- |
| **Logic** | Heuristic (Strongest Signal) | Balances ease-of-use with Git robustness. |
| **Naming** | Manual / Explicit | Removes dependencies on complex pre-flight containers and Auth. |
| **Safety** | Explicit \`--branch\` always wins | Provides an escape hatch for cases where the heuristic might fail. |
| **Reliability** | "What you type is what you get" | Prevents confusion from unpredictable AI slug generation. |
