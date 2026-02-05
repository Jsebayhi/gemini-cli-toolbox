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

We have implemented a deterministic resolution hierarchy that combines explicit flags, auto-detection, and AI-powered inference.

### 1. The Priority Matrix
When `--worktree` is enabled, the Git reference is resolved using the following priority:

| Input Pattern | Logic Applied | Resulting Branch | Resulting Task |
| :--- | :--- | :--- | :--- |
| `--branch X ...` | **Explicit Override** | `X` | Remaining Args |
| `[Existing Branch] ...` | **Auto-Detection** | `[Existing Branch]` | Remaining Args |
| `[Task String] ...` | **AI Naming** | `ai-generated-slug` | `[Task String]` |
| (No arguments) | **Safe Default** | `Detached HEAD` | None |

### 2. The Syntactic Heuristic (Non-Consuming Peek)
To avoid brittle keyword lists (which require constant updates as the CLI subcommands grow), the parser uses a "strongest signal" heuristic:
1.  **Peek:** The tool peeks at the first positional argument.
2.  **Verify:** It checks if this argument matches an existing local branch (via `git show-ref`).
3.  **Result:**
    *   **If Branch exists:** It is consumed as the **Context**. The remaining arguments are passed to the agent.
    *   **If Branch does NOT exist:** The entire argument list is treated as the **Intent**, triggering the Pre-Flight AI naming logic.
    *   **Fallback:** If the argument contains spaces, it is automatically treated as an **Intent** (Task), bypassing the branch check.

### 3. Pre-Flight AI Naming (Gemini 2.5 Flash)
When a task is provided without an explicit branch, the CLI performs a one-shot call to **Gemini 2.5 Flash**.
*   **Performance:** Using a "Flash" model ensures this naming step is sub-second.
*   **System Instruction:** *"You are a git branch naming utility. Slugify the input task into a concise branch name. Return ONLY the slug. Do not analyze the codebase or provide explanations."*
*   **Resumability:** If the AI generates a name that already exists in the worktree cache, the tool automatically reuses the existing worktree, enabling resumable multi-session tasks.

## User Journeys

*   **The Fresh Start:** `gemini-toolbox --worktree "Refactor the auth models"` -> AI creates `refactor-auth-models` branch.
*   **The PR Repair (Resumable):** `gemini-toolbox --worktree fix/bug-123 chat` -> Tool detects branch, sets up worktree, and starts interactive chat.
*   **The Explicit Context:** `gemini-toolbox --worktree --branch feat/ui "Fix buttons"` -> Guaranteed to use `feat/ui` regardless of whether the prompt mentions other branches.
*   **The Named Monitoring Session:** `gemini-toolbox --worktree "Monitoring the CI failures"` -> Creates a named workspace for an interactive session, allowing the user to return to the same context later.
*   **Safe Exploration:** `gemini-toolbox --worktree` (No args) -> Creates a detached HEAD worktree.

## Alternatives Considered (Rejected)

### 1. Hardcoded Reserved Keywords
*   **Idea:** Ignore common commands like `chat`, `hooks`, or `update` when parsing branches.
*   **Reason for Rejection:** Too brittle. Requires manual updates whenever the `gemini-cli` adds new subcommands.

### 2. Mandatory CLI Terminator (`--`)
*   **Idea:** Force users to separate worktree branch from task using `--`.
*   **Reason for Rejection:** Poor UX. Users often forget the terminator, leading to the "branch named 'chat'" bug.

### 3. UUID-Only Branch Naming
*   **Idea:** Generate random branch names for every worktree.
*   **Reason for Rejection:** Makes the Hub and filesystem impossible to navigate for humans. Semantic names provide critical context.

## Trade-offs and Arbitrages

| Feature | Decision | Rationale |
| :--- | :--- | :--- |
| **Logic** | Heuristic (Strongest Signal) | Balances ease-of-use with Git robustness. |
| **AI Model** | Gemini 2.5 Flash | Ensures the naming call doesn't slow down session startup. |
| **Safety** | Explicit `--branch` always wins | Provides an escape hatch for cases where the heuristic might fail. |
| **Naming** | Semantic over Random | Improves navigability of the worktree cache. |