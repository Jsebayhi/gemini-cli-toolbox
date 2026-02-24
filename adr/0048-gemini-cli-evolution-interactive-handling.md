# ADR 0048: Gemini CLI Evolution: Interactive-by-Default Handling

Date: 2026-02-24
Status: Proposed
Issue: [99](https://github.com/Jsebayhi/gemini-cli-toolbox/issues/99)

## Context
The `gemini-cli` (the core agent inside the toolbox) has changed its session handling. Previously, passing a task as a positional argument (e.g., `gemini "Refactor auth"`) would trigger a non-interactive, headless execution that terminates upon completion. 

With the latest version, **interactive mode is the new default**. Any query passed as a positional argument now launches a persistent interactive session. Non-interactive (headless) mode now explicitly requires the `-p/--prompt` flag.

Our current implementation of `gemini-toolbox` and `gemini-hub` relies on the old behavior for "one-shot" or autonomous tasks (e.g., the Hub's "Bot Mode"). This means these tasks will now incorrectly start an interactive `tmux` session inside the container, keeping it alive even after the task is done, which wastes resources and deviates from user intent.

## Decision
We will update the toolbox and hub to align with the CLI's new interactive-by-default behavior.

### 1. Gemini Toolbox Flag Expansion
We will add `--prompt / -p` to `gemini-toolbox`. This flag will be forwarded directly to the CLI inside the container to trigger non-interactive mode.

### 2. Gemini Hub Launcher Update
The `LauncherService` in the Hub will be updated to inject the `-p` flag instead of using positional arguments when the `interactive` toggle is unchecked.

### 3. Documentation Alignment
All user-facing documentation (`README.md`, `USER_GUIDE.md`, and `completions/`) will be updated to reflect that one-shot tasks now require the `--prompt` flag.

## Alternatives Considered

### Alternative 1: Explicit Flag Mapping (Selected)
*   **Description:** Directly expose and use the CLI's new `-p/--prompt` flag in the toolbox wrapper.
*   **Pros:** Minimal friction, aligns with upstream CLI conventions, simple to implement.
*   **Cons:** Requires user awareness of the new flag for one-shot tasks.

### Alternative 2: Automatic Task Detection (Non-selected)
*   **Description:** Attempt to detect if the session *should* be non-interactive based on the presence of a positional task and auto-inject `-p`.
*   **Pros:** Maintains backward compatibility for positional arguments.
*   **Cons:** Brittle; conflicts with the CLI's new intent (which allows starting an interactive session with an initial query). It would create confusion if a user *wants* an interactive session with an initial prompt.
*   **Reason for Rejection:** The upstream CLI choice is deliberate. Attempting to override it with "smart" detection would lead to inconsistent behavior compared to the raw CLI.

### Alternative 3: Command-based Execution (Non-selected)
*   **Description:** Introduce a new command like `gemini-toolbox run "task"` specifically for non-interactive execution.
*   **Pros:** Clear semantic separation between "chat" and "run".
*   **Cons:** Diverges from the `gemini` CLI's own flag-based approach, adds more boilerplate to the wrapper.
*   **Reason for Rejection:** Unnecessary complexity. `gemini-toolbox` is primarily a thin wrapper, and keeping the interface consistent with the underlying tool is more idiomatic.

## Consequences

### Positive
*   **Resource Efficiency:** Autonomous Hub tasks will correctly terminate once finished.
*   **Consistency:** The toolbox remains a faithful wrapper of the underlying CLI.
*   **Stability:** Avoids brittle "smart" detection logic.

### Negative
*   **Breaking Change:** Users who relied on positional arguments for one-shot tasks in the CLI (via the toolbox) will now need to add `--prompt`. We mitigate this through updated documentation.
