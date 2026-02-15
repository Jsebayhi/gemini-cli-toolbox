# Bash Testing Guidelines

## 1. Framework
*   **Bats-core:** We use `bats-core` for testing.
*   **Location:** Tests reside in `tests/bash/`.
*   **Running:** Use `make test-bash`.

## 2. Test Types
*   **Unit Tests:** Source the script (which requires the "Main Function Pattern") and test individual functions.
*   **Integration Tests:** Run the script as an executable to verify end-to-end behavior (argument parsing, exit codes).

## 3. Mocking
*   **Strategy:** Use `test_helper.bash` to override `PATH` and inject mock binaries (e.g., `docker`, `git`).
*   **Fidelity:** Mocks MUST preserve argument quoting. Use `"$@"` or `printf` loops in your mock scripts, not `$*`.
*   **State:** Reset global variables in `setup()` if sourcing scripts.

## 4. Environment
*   **Runner:** Tests run in a Debian-based container (`gemini-bash-tester`).
*   **Dependencies:** External libraries (`bats-support`, `bats-assert`) are downloaded via `make` targets and ignored by git.
