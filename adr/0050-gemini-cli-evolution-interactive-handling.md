# ADR-0050: Gemini CLI Evolution: Interactive-by-Default Handling

Date: 2026-02-24
Status: Proposed
Issue: [99](https://github.com/Jsebayhi/gemini-cli-toolbox/issues/99)

## Context
The `gemini-cli` (the core agent inside the toolbox) has changed its session handling. Previously, passing a task as a positional argument (e.g., `gemini "Refactor auth"`) would trigger a non-interactive, headless execution that terminates upon completion. 

With the latest version, **interactive mode is the new default**. Any query passed as a positional argument now launches a persistent interactive session. Non-interactive (headless) mode now explicitly requires the `-p/--prompt` flag.

Our current implementation of `gemini-toolbox` and `gemini-hub` relies on the old behavior for "one-shot" or autonomous tasks (e.g., the Hub's "Bot Mode"). This means these tasks will now incorrectly start an interactive `tmux` session inside the container, keeping it alive even after the task is done, which wastes resources and deviates from user intent.

## Decision
We will align the toolbox and hub with the CLI's new interactive-by-default behavior by delegating flag handling to the underlying tool.

### 1. Minimal Wrapper Design
We explicitly **reject** adding \`--prompt / -p\` as first-class flags to the \`gemini-toolbox\` wrapper. This ensures the wrapper remains lean and doesn't need to be updated for every upstream CLI change. Users should use the standard \`--\` separator to pass application-specific flags (e.g., \`gemini-toolbox -- -p "task"\`).

### 2. Gemini Hub Launcher Update
The \`LauncherService\` in the Hub will be updated to inject the \`-p\` flag directly into the application arguments (after \`--\`) when the \`interactive\` toggle is unchecked.

### 3. Documentation Alignment
All user-facing documentation (\`README.md\`, \`USER_GUIDE.md\`, and \`completions/\`) will be updated to reflect that one-shot tasks now require passing \`-p\` via application arguments.

## Alternatives Considered

### Alternative 1: Explicit Flag Mapping (Rejected)
*   **Description:** Directly expose and use the CLI's new \`-p/--prompt\` flag in the toolbox wrapper.
*   **Pros:** Slightly shorter command for the user.
*   **Cons:** Increases wrapper complexity, introduces maintenance debt for upstream changes.
*   **Reason for Rejection:** Deviates from the "lean wrapper" philosophy. The underlying CLI's flags are already accessible via \`--\`.

### Alternative 2: Automatic Task Detection (Rejected)
*   **Description:** Attempt to detect if the session *should* be non-interactive based on the presence of a positional task and auto-inject \`-p\`.
*   **Pros:** Maintains backward compatibility for positional arguments.
*   **Cons:** Brittle; conflicts with the CLI's new intent (which allows starting an interactive session with an initial query). We are not responsible for mitigating breaking changes made by the upstream \`gemini-cli\`.
*   **Reason for Rejection:** The upstream CLI choice is deliberate. Attempting to override it with "smart" detection would lead to inconsistent behavior compared to the raw CLI and introduce maintenance overhead.

### Alternative 3: Command-based Execution (Rejected)
*   **Description:** Introduce a new command like \`gemini-toolbox run "task"\` specifically for non-interactive execution.
*   **Pros:** Clear semantic separation between "chat" and "run".
*   **Cons:** Diverges from the \`gemini\` CLI's own flag-based approach, adds more boilerplate to the wrapper.
*   **Reason for Rejection:** Unnecessary complexity.

### Alternative 4: Positional Argument Forwarding (Selected)
*   **Description:** Leverage the existing positional argument forwarding (\`--\`) to allow users to pass \`-p\` directly to the CLI.
*   **Pros:** Zero maintenance, strictly follows upstream CLI conventions, keeps the wrapper clean.
*   **Cons:** Users must learn to use the \`-- -p\` pattern for non-interactive tasks.


## Consequences

### Positive
*   **Resource Efficiency:** Autonomous Hub tasks will correctly terminate once finished.
*   **Consistency:** The toolbox remains a faithful wrapper of the underlying CLI.
*   **Stability:** Avoids brittle "smart" detection logic.

### Negative
*   **Breaking Change:** Users who relied on positional arguments for one-shot tasks in the CLI (via the toolbox) will now need to add `--prompt`. We mitigate this through updated documentation.
