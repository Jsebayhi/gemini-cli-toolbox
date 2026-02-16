# 0040. Bash Coverage Metrics

## Status
Proposed

## Context
While we have high test coverage for the Python Hub, our core Bash scripts (`gemini-toolbox`, `gemini-hub`) lack visibility into their test execution paths. We need a way to measure and report Bash coverage to ensure our journey tests are as exhaustive as intended.

## Alternatives Considered

### Naive kcov Integration
*   **Description:** Install `kcov` in the test runner and manually run it via `make`.
*   **Pros:** Minimal setup.
*   **Cons:** No automated reporting; results are static HTML files that are difficult to inspect in a CLI-first environment.
*   **Status:** Rejected
*   **Reason for Rejection:** Doesn't provide enough immediate value to the developer during `local-ci`.

### External SaaS Coverage (e.g., Codecov)
*   **Description:** Upload `kcov` output to an external service for tracking and visualization.
*   **Pros:** Professional dashboard; history tracking.
*   **Cons:** Requires API keys and internet access; adds external dependency to the CI pipeline.
*   **Status:** Rejected
*   **Reason for Rejection:** Overkill for our current scale and violates the "offline-friendly" feel of `local-ci`.

### Integrated CLI Metrics (Selected)
*   **Description:** Build `kcov` into the `gemini-bash-tester` image, wrap the `bats` execution in the `Makefile`, and use a small helper to print the coverage summary directly to the terminal.
*   **Pros:** Native integration with `local-ci`; immediate feedback; no external dependencies.
*   **Cons:** Requires building `kcov` from source in the Dockerfile (as it's often missing or outdated in standard repos).
*   **Status:** Selected
*   **Reason for Selection:** Best balance of visibility and simplicity. It allows us to fail the build if coverage drops, just like we do for the Hub.

## Decision
Integrate `kcov` into the `gemini-bash-tester` container and update the `Makefile` to report Bash coverage during every test run.

## Consequences
*   **Positive:** Improved visibility into Bash script quality; easier to identify dead code or untested edge cases.
*   **Negative:** Building the test runner image will take longer (compiling `kcov`); requires `--cap-add=SYS_PTRACE` for the test container.
