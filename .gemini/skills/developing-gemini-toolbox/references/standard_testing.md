# Standard Testing Best Practices (Unit & Integration)

We adhere to the "Testing Trophy" model, prioritizing integration tests while maintaining a solid foundation of unit tests and essential E2E smoke tests.

## 1. The Testing Trophy
- **Static (Base):** Types and linting (handled by Ruff/Mypy).
- **Unit (Smallest):** Reserved for complex algorithmic logic or data parsing.
- **Integration (Bulk):** The majority of the suite. Tests API endpoints and service interactions.
- **E2E (Top):** Critical user journeys only (e.g., full session launch).

## 2. Mocking Principles
- **System Boundaries Only:** Mock only slow, non-deterministic, or dangerous external boundaries (e.g., `subprocess.run`, `requests.get`, `time.sleep`).
- **No Internal Mocks:** Do NOT mock internal services or helper classes. Let the code execute through the full stack.
- **No Filesystem Mocks:** Never mock `os.listdir`, `open()`, or `pathlib`. 
    - **Pattern:** Use the standard `tmp_path` fixture to create real directory structures on disk.

## 3. Coverage & Quality
- **Mandatory Threshold:** Every component MUST maintain at least **90% coverage**.
- **Parallel Collection:** When running in parallel (via `pytest-xdist`), ensure a `.coveragerc` with `parallel = True` is present to correctly merge data from all workers.
- **One Logical Assertion:** Follow the rule of one logical check per test to ensure clear failure causes.

## 4. Automation
- **Target Seperation:** The standard `make test` should be fast. Slower tests (like UI/E2E) should be moved to a separate target (e.g., `make test-ui`).
- **Clean Slate:** Ensure database states, caches, and file structures are cleared or namespaced between every test run.
