# 0036. Session Lifecycle Management (Stop)

## Status
Proposed

## Context
Users currently need to use raw `docker stop` commands to terminate Gemini sessions. This is cumbersome and requires knowledge of Docker internals. We need a native way to stop sessions both from the CLI and the Hub UI.

## Alternatives Considered

### [Strict ID-only Stop]
*   **Description:** The `stop` command only accepts the full unique Session ID.
*   **Pros:** Minimal risk of accidental stops.
*   **Cons:** Poor user experience; session IDs are generated and not easily memorable.
*   **Status:** Rejected
*   **Reason for Rejection:** Does not satisfy the requirement to allow stopping by project name.

### [Hub-only Stop]
*   **Description:** Lifecycle management is exclusively handled through the Gemini Hub web interface.
*   **Pros:** Simplifies the CLI; centralized session management.
*   **Cons:** Breaks the CLI-first workflow; requires the Hub to be running even for simple local cleanup.
*   **Status:** Rejected
*   **Reason for Rejection:** Fails to meet the explicit requirement for a CLI `stop` command.

### [Smart Matching with Ambiguity Guard (Selected)]
*   **Description:** The `stop` command and Hub UI allow stopping sessions by ID or project name. If a project name matches multiple active sessions, the command will refuse to stop them and instead list the matches, requiring the user to specify a full session ID.
*   **Pros:** High flexibility; intuitive UX for unique sessions; prevents accidental mass-termination of unrelated sessions.
*   **Cons:** Requires an extra step if multiple sessions for the same project are active.
*   **Status:** Selected
*   **Reason for Selection:** Best balance between convenience and safety.

## Decision
Implement a `stop` command in `bin/gemini-toolbox` and a corresponding API/UI in `gemini-hub`. 

The CLI will:
1. If no argument is provided, default to the current project name.
2. Check for an exact match on the provided ID.
3. If no exact match, search for containers matching `gem-<input>-*`.
4. If exactly one match is found, stop it.
5. If multiple matches are found, list them and exit with an error.
6. Execute `docker stop` on the resolved ID.

The Hub will:
1. Expose a `POST /api/sessions/stop` endpoint.
2. Use the `LauncherService` (or similar) to execute the stop command.
3. Update the UI to include a "Stop" button on session cards.

## Consequences
*   **Positive:** Improved user experience for session cleanup.
*   **Positive:** Better resource management through easier termination of idle sessions.
*   **Negative:** Requires maintaining container naming consistency to ensure accurate matching.
