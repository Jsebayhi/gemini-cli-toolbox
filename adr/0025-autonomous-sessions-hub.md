# 25. Autonomous Sessions in Hub

Date: 2026-02-01
Status: Accepted

## Context
The Gemini CLI supports autonomous operation by passing a task directly to the command (e.g., `gemini "do something"`). Users want to trigger this behavior from the Gemini Hub without manually opening a terminal. This is referred to as "Autonomous Mode" or "Bot Mode".

## Decision
We will extend the Gemini Hub launch API and UI to support an optional `task` parameter and an `interactive` mode toggle.

### 1. API Extension
The `/api/launch` endpoint now accepts:
*   `task` (string, optional): The instruction for the agent.
*   `interactive` (boolean, default: `true`): Whether to keep the session open for user input after the task is sent.

### 2. Toolbox Command Construction
The Hub constructs the `gemini-toolbox` command based on these parameters:

*   **Task + Interactive:** `gemini-toolbox ... -- -i "the task"`
*   **Task Only (Non-interactive):** `gemini-toolbox ... -- -p "the task"`
*   **No Task:** `gemini-toolbox ...` (Standard interactive shell)

### 3. UI Integration
*   A new "Initial Task" textarea is added to the Launch Wizard.
*   An "Interactive" checkbox allows users to choose between one-shot execution and interactive sessions.
*   The UI enforces that non-interactive mode requires a task to be present.

## Consequences

### Positive
*   **Convenience:** Users can launch bots directly from the web dashboard.
*   **Consistency:** Leverages the existing CLI argument structure (`-i` flag).
*   **Safety via Isolation:** The autonomous agent runs inside a Docker container. Its file access is strictly limited to the mounted project volume, preventing any modification to the host system outside the target project.

### Negative
*   **Direct Modification:** The agent will modify files in the mounted directory immediately upon launch. This is the intended behavior, but users must be aware that the "Bot" is active from the start.