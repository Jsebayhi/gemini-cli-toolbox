# ADR 0030: Automatic Task-Based Branch Naming (Rejected)

## Status
Rejected

## Context
When creating a new worktree from a task description (e.g., `gemini-toolbox --worktree "Refactor the auth logic"`), we explored using an LLM to automatically generate a concise branch slug (e.g., `refactor-auth-logic`). The goal was to provide a "zero-config" experience where the user only provides an intent, and the tool handles the Git management.

## Exploration Phase: The "Smart" Resolution
We initially implemented a multi-stage resolution logic:
1.  **Syntactic Heuristic**: Peeked at the first positional argument. If it matched an existing branch, use it. Otherwise, assume it's part of a task description.
2.  **Context-Aware Naming**: To improve slug quality, we provided the naming agent with a **Read-Only mount** of the project and set the working directory. This allowed the AI to see the project type (e.g., Python vs C++) to generate semantic names.
3.  **Environment Parity**: We attempted to propagate all `EXTRA_DOCKER_ARGS` (proxies, API keys, local extensions) to this "Pre-flight" naming container.

## Rationale for Rejection
Despite the sophisticated implementation, the feature was rejected due to several critical flaws discovered during real-world testing:

### 1. The "Fragile Chain" Problem
The naming container became a mandatory "Gatekeeper." If the user needed to re-authenticate with the Gemini CLI, the naming call would fail cryptically before the actual session even started. This introduced a dependency on Auth, Network, and Docker for a simple string-slugification task.

### 2. Path & Character Hallucinations
The LLM occasionally returned slugs containing unexpected characters (e.g., `feature-auth'''`) or markdown formatting. This resulted in the creation of filesystem folders with literal single-quotes or backticks in their names, making them difficult to manage or delete via standard shell commands.

### 3. Ambiguity & The "Branch Named 'Fix'" Bug
The syntactic heuristic (peeking at the first arg) was inherently unreliable. A user prompt like `"Fix the login bug"` would frequently be misinterpreted as a request to create a branch named `Fix`, forcing the user to use the `--` terminator which defeated the "zero-config" goal.

### 4. Security Attack Surface
Mounting the project (even in Read-Only mode) just to generate a branch name was deemed an unnecessary security risk. It gave a "pre-flight" agent access to source code before the user had a chance to verify the session's sandbox settings.

## Final Decision
We have rejected the automatic task-based branch naming feature to simplify future maintenance and ensure system stability. The potential UX benefits did not outweigh the long-term operational costs and the risk of unpredictable behavior in production environments.

## Trade-offs Summary

| Aspect | AI Naming (Rejected) | Explicit Naming (Accepted) |
| :--- | :--- | :--- |
| **User Effort** | Low (Automatic) | Medium (Manual Flag) |
| **Reliability** | Low (Auth/LLM dependent) | High (Deterministic) |
| **Security** | Lower (Requires RO Mount) | Higher (Air-gapped naming) |
| **Predictability** | Low (Hallucinations) | High (Exact) |