# Python Testing Implementation Standards

This document defines how to apply general testing principles specifically using the Python toolchain.

## 1. Toolchain
- **Runner:** Use `pytest` as the primary test runner.
- **Plugins:** 
    - `pytest-mock`: For `unittest.mock` integration.
    - `pytest-xdist`: For parallel test execution.
    - `pytest-cov`: For coverage reporting.

## 2. Parallelism & Thread Safety
- **Mandatory Parallelism:** Run tests using `pytest -n auto`.
- **Monkeypatching:** Use the `monkeypatch` fixture to override global state (Config attributes, Environment variables) safely. NEVER mutate class attributes directly.
- **Process Isolation:** Assume every test runs in a dedicated worker process.

## 3. Mocking Implementation
- **Boundary Mocking:** Use `unittest.mock.patch` to stub out `subprocess.run` or `requests`.
- **Filesystem Testing:** Use the `tmp_path` fixture to create real files/directories on the container's disk. DO NOT mock `os.path` or `open`.

## 4. Quality & Coverage
- **Threshold:** Every component must exceed **90% coverage**.
- **Accurate Reporting:** A `.coveragerc` file with `parallel = True` MUST be present to ensure coverage data from parallel workers is correctly merged.
- **Log Hygiene:** Use a `suppress_logs` fixture (adjusting levels to `CRITICAL`) when testing expected error paths to keep CI logs clean.

## 5. Dependency Scoping
- **Isolated Testing Stack:** Maintain a `requirements-test.txt` file for testing-only dependencies (Pytest, Mocks, etc.) to keep production images slim.
