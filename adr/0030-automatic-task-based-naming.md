# ADR 0030: Automatic Task-Based Branch Naming

## Status
Rejected

## Context
When creating a new worktree from a task description (e.g., `gemini-toolbox --worktree "Refactor the auth logic"`), we considered using an LLM to automatically generate a concise branch slug (e.g., `refactor-auth-logic`) to save the user from manually typing a name.

## Decision
We rejected the use of an automated "Pre-Flight" AI naming container.

## Rationale
1.  **Fragility:** The naming container requires the full environment context (API keys, proxies, network mode) to function. Propagating this state correctly for a sub-second operation introduced significant complexity and potential failure points (e.g., if the user needs to re-authenticate).
2.  **Unpredictability:** Users reported confusion when the generated name did not match their mental model or contained unexpected characters.
3.  **Security:** To generate high-quality names, the agent needed Read-Only access to the project source code, which unnecessarily increased the attack surface for a simple naming operation.
4.  **UX Friction:** If the naming call fails (e.g., due to network issues), the user is left waiting or receives a fallback name (`gem-task-UUID`) which is worse than just asking them to provide a name.

## Alternatives Accepted
We adopted **Manual Explicit Naming** (ADR 0028):
*   **Mechanism:** The first positional argument is treated as the branch name.
*   **Philosophy:** "What you type is what you get."
*   **Example:** `gemini-toolbox --worktree fix-auth "Refactor the logic"` -> Creates branch `fix-auth`.
