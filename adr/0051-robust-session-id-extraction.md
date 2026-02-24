# ADR-0051: Robust Session ID Extraction for Hub Integration

## Status
Accepted

## Context
Following the implementation of ADR-0042 (Standardized Bash Logging), all informational messages in `gemini-toolbox` were moved to `stderr`. This included the "Container started: <ID>" message. 

The Gemini Hub UI relies on extracting this ID from the process output to provide a direct "Connect" link to the user. Because it was looking only at `stdout`, the link disappeared, degrading the user experience.

## Alternatives Considered

### [Alternative 1: Move session ID to Stdout]
*   **Description:** Use `echo` instead of `log_info` for the session ID.
*   **Pros:** Adheres to the "stdout for functional data" principle.
*   **Cons:** Risk of accidental capture if `main` is ever sourced or used in a way where `stdout` is piped. Potential for future maintainers to "fix" it back to `log_info` due to lack of context.

### [Alternative 2: Robust Frontend Scanning (Selected)]
*   **Description:** Keep the session ID in `stderr` (via `log_info`) but update the Gemini Hub frontend to scan both `stdout` and `stderr` for the ID.
*   **Pros:** Maintains logging consistency in the toolbox. Avoids potential capture issues in Bash. Robust against future logging changes.
*   **Cons:** Slightly more complex regex logic in the frontend.

## Decision
We will prioritize logging consistency in the toolbox and implement robustness in the consumer. The Gemini Hub UI will be updated to scan both `stdout` and `stderr` streams for the "Container started" pattern.

## Consequences
*   **Positive:** Restores the "Connect" button in the Hub. Maintains a clean, consistent logging pattern in `bin/gemini-toolbox`.
*   **Negative:** None identified.
