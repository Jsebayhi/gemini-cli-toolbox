# 0037. Bash Automated Testing

## Status
Proposed

## Context
The core bash scripts (`bin/gemini-toolbox` and `bin/gemini-hub`) are critical components of the toolbox but currently lack any automated testing. This makes it difficult to ensure regressions are not introduced, refactor code safely, and verify complex logic like path resolution and dynamic tagging.

## Alternatives Considered

### Naive Shell-based Testing
*   **Description:** Create custom `.sh` test scripts that invoke the target commands and use standard shell conditionals (`if/then/else`) to verify results.
*   **Pros:** Zero external dependencies; extremely fast; easy for shell users to understand.
*   **Cons:** High boilerplate for mocking and assertions; poor error reporting; lack of standardized structure.
*   **Status:** Rejected
*   **Reason for Rejection:** Not robust enough for a growing codebase. The manual effort to implement reliable mocking and clear error output would eventually lead to a reinvented (and likely inferior) testing framework.

### Python-based Integration Testing (pytest)
*   **Description:** Use `pytest` to invoke bash scripts as subprocesses, leveraging Python's powerful mocking and assertion libraries.
*   **Pros:** Access to a rich ecosystem; consistent with the testing approach used in the Gemini Hub; easy to test cross-component interactions.
*   **Cons:** Higher overhead; requires a Python environment; disconnect between the script language (Bash) and the test language (Python).
*   **Status:** Rejected
*   **Reason for Rejection:** Overkill for unit testing shell logic. Bash scripts are best tested in an environment that understands shell semantics (like variable expansion and stream redirection) natively.

### Bats-core Framework (Selected)
*   **Description:** Use `bats-core` (Bash Automated Testing System) along with `bats-support` and `bats-assert`.
*   **Pros:** Industry standard for shell testing; TAP-compliant output; powerful assertion libraries; allows tests to be written in a syntax very close to standard Bash.
*   **Cons:** Adds a new tool dependency (`bats`).
*   **Status:** Selected
*   **Reason for Selection:** Bats-core provides the right level of abstraction for testing bash scripts. It is lightweight yet powerful, and its widespread adoption ensures maintainability and community support.

## Decision
Adopt `bats-core` as the standard testing framework for bash scripts in the Gemini CLI Toolbox.

## Consequences
*   **Positive:** Improved reliability and confidence when modifying core scripts; clearer documentation of script behavior through tests; standardized testing process.
*   **Negative:** Developers need to install `bats-core` locally to run tests (or use a provided containerized test runner).
