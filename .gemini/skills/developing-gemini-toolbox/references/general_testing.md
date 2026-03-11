# General Testing Standards (Language Agnostic)

These principles apply to all components in the Gemini CLI Toolbox, regardless of the implementation language.

## 1. The Testing Trophy
We prioritize tests that provide the highest confidence-to-cost ratio.
- **Static Analysis:** Linters and type checkers are mandatory.
- **Integration Tests:** The bulk of the suite. Verify service interfaces and system boundaries.
- **Contract Testing:** Enforce JSON Schemas for all API interactions. Verify that mocks used in UI tests match the actual schemas produced by the backend to prevent "Silent Breakage."

## 2. Mocking Philosophy
- **Mock at the Boundary:** Only mock slow, non-deterministic, or dangerous external systems.
- **Favor Realism:** Do not mock internal services. Let the code execute through the full stack.
- **Golden Files:** For complex CLI outputs, use "Golden Data" snapshots from the real system instead of manually writing mock strings.

## 3. Test Qualities
- **Atomicity:** Each test verifies a single logical outcome.
- **Synchronization:** Use polling/probes to ensure services are ready before starting tests (avoid "Socket Race" conditions).
- **Clean Slate:** Every test starts with a fresh environment.
- **Parallel Readiness:** NEVER mutate global shared state. Use local overrides or scoped fixtures.

## 4. Idempotency & Isolation Mandates
As the test suite grows, maintaining complete isolation between test cases is critical. Tests that leak state (filesystem changes, global configuration modifications, or persistent Docker containers) cause flaky builds and order-dependency.

### Python (Pytest) Standards
- **No Direct `Config` Modification:** Never modify `Config` attributes directly (e.g., `Config.FOO = True`). Always use the `monkeypatch` fixture or `mocker.patch.object`.
- **Filesystem Isolation:** Always use the `tmp_path` fixture for any test that requires reading or writing files.
- **Mocking System Calls:** Always mock `subprocess.run`, `os.kill`, and other side-effect-heavy system calls unless specifically writing an integration test.

### Bash (Bats) Standards
- **Centralized Setup:** Use `setup_test_env` in every `.bats` file to create a unique `TEST_TEMP_DIR` and redirect `HOME`.
- **Automatic Teardown:** Use `teardown_test_env` to ensure `TEST_TEMP_DIR` is removed.
- **Local State Only:** If a test requires a directory outside of `TEST_TEMP_DIR` (e.g., to test git-root discovery failure), it must be created in a way that guarantees cleanup (e.g., using a `trap 'rm -rf "$dir"' EXIT` within the test subshell).
