# Software Engineering Standards: Gemini Hub

This document defines the architectural and coding standards for the `gemini-hub` component. All agents and developers modifying this codebase must adhere to these guidelines to ensure maintainability, scalability, and robustness.

## 1. Architectural Patterns

### 1.1 Modular Structure
Do not add code to a monolithic `app.py`. The application is structured by **domain** and **layer**:

*   **`app/`**: The Python package root.
*   **`app/api/`**: JSON endpoints (REST). Logic here deals with request parsing and response formatting.
*   **`app/web/`**: HTML rendering (Jinja2). Logic here deals with UI presentation.
*   **`app/services/`**: Pure business logic (e.g., parsing Tailscale output, managing subprocesses). **These modules must not depend on Flask.**
*   **`app/static/` & `app/templates/`**: Standard Flask locations for assets and HTML.

### 1.2 The App Factory Pattern
Global application objects are prohibited. Use the Application Factory pattern to create the Flask instance.
*   **Why:** Enables easy unit testing and prevents circular imports.
*   **Pattern:**
    ```python
    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)
        # Register Blueprints...
        return app
    ```

## 2. Coding Standards

### 2.1 Type Hinting
All function signatures must use Python 3 type hints.
*   **Goal:** Self-documenting code and static analysis compatibility.
*   **Example:**
    ```python
    from typing import List, Dict, Any

    def parse_peers(status: Dict[str, Any]) -> List[Dict[str, Any]]:
        # ...
    ```

### 2.2 Configuration Management
*   **Centralization:** Do not use `os.environ.get()` inside business logic. Use a central `Config` class (e.g., in `config.py`) to load and validate all environment variables at startup.
*   **Fail Fast:** The application should crash immediately on startup if a required variable (like `TAILSCALE_AUTH_KEY` for a prod run) is missing, rather than failing silently later.

### 2.3 Subprocess Safety
When executing shell commands (e.g., `gemini-toolbox`, `tailscale`):
*   **Avoid `shell=True`:** Always use a list of arguments `["cmd", "arg"]` to prevent injection vulnerabilities.
*   **Timeout:** Always specify a `timeout` in `subprocess.run` to prevent hanging processes.
*   **Error Handling:** Always check `result.returncode` or use `check=True`.

### 2.4 Service Granularity (Size & Scope)
*   **Single Responsibility:** A service must focus on a single business domain (e.g., `TailscaleService` for VPN status, `LauncherService` for process execution). If you describe a service's purpose using "and" (e.g., "Manages VPN **and** renders HTML"), it must be split.
*   **Size Limit:** A service file exceeding **300 lines** is a code smell. Refactor it into sub-modules or helper classes.
*   **Cognitive Load:** A developer should be able to understand the entire service's public API in under 2 minutes.

### 2.5 Observability & Logging
*   **No `print()`:** Usage of `print()` for debugging is strictly forbidden in production code. Use the standard `logging` module.
*   **Levels:** Use `logging.info()` for lifecycle events and `logging.error()` for failures.
*   **Context:** Log messages must include relevant context (e.g., `[Project: my-app] Failed to launch`).

### 2.6 Error Handling
*   **Custom Exceptions:** Define domain-specific exceptions (e.g., `TailscaleConnectionError`) in an `exceptions.py` module rather than raising generic `Exception` or `RuntimeError`.
*   **Bubble Up:** Services should raise exceptions, not swallow them. The API/Web layer is responsible for catching them and returning 400/500 responses.

## 3. Dependency Management

### 3.1 Explicit Dependencies
*   **Manifest:** All Python dependencies must be listed in `requirements.txt`.
*   **Pinning:** Versions must be pinned (e.g., `Flask==3.0.0`) to ensure reproducible builds.
*   **Dockerfile:** The Dockerfile must install from this file (`pip install -r requirements.txt`) rather than ad-hoc packages.

## 4. Frontend Standards

### 4.1 Separation of Concerns
*   **No Inline HTML:** Do not return HTML strings from Python functions. Use `render_template`.
*   **Assets:** CSS and JS should reside in `static/`, not embedded in `<style>` tags within the HTML templates (unless critical for a single-file prototype, which we are moving away from).

## 5. Testing Strategy

### 5.1 Framework & Tools
*   **Runner:** Use `pytest` as the standard test runner.
*   **Plugins:** Use `pytest-flask` for testing API routes and `pytest-mock` for mocking dependencies.
*   **Coverage:** Use `pytest-cov` to measure code coverage.

### 5.2 Directory Structure
Mirror the application structure within a `tests/` directory at the project root:
```text
tests/
├── conftest.py          # Shared fixtures (e.g., app instance, mock config)
├── unit/                # Fast, isolated tests
│   ├── test_services.py
│   └── ...
└── integration/         # Tests involving the Flask context
    ├── test_api_routes.py
    └── ...
```

### 5.3 Unit Testing Rules
*   **Target:** Focus on `app/services/` and utility functions.
*   **Isolation:** Unit tests **must not** perform IO operations (network requests, file system writes, subprocess execution).
*   **Mocking:** Use `unittest.mock` or `pytest-mock` to stub out external systems (e.g., `subprocess.run`, `tailscale` CLI calls).
*   **Atomicity:** Follow the "One Logical Assertion" rule. Do not group multiple unrelated checks into a single test. If a function has three distinct outcomes, write three distinct tests (e.g., `test_launch_success`, `test_launch_failure_permission`, `test_launch_failure_timeout`).
*   **Speed:** The entire unit test suite should run in under 2 seconds.

### 5.4 Integration Testing Rules
*   **Target:** Focus on `app/api/` and `app/web/`.
*   **Context:** Use the `client` fixture provided by `pytest-flask` to simulate HTTP requests.
*   **Scope:** Verify that the correct status codes (200, 400, 500) and JSON structures are returned for valid and invalid inputs.

### 5.5 Coverage Mandates
While we follow the Testing Trophy, we still enforce high coverage standards to prevent regressions:
*   **API Routes:** **100% coverage** is mandatory for all route handlers (testing happy paths, validation errors, and server errors).
*   **Business Logic:** **90% coverage** is required for all modules in `app/services/`.
*   **Utilities:** **100% coverage** for pure helper functions and data parsers.

### 5.6 Testing Philosophy (The "Testing Trophy")
*   **The Concept:** We subscribe to the "Testing Trophy" model (popularized by Kent C. Dodds) rather than the traditional "Testing Pyramid".
    *   **Static (Types/Linting):** The foundation. (Handled by `ruff` and `mypy`).
    *   **Unit Tests (Smallest):** Keep them for complex algorithmic logic (e.g., parsing weird Tailscale JSON).
    *   **Integration Tests (The Bulk):** Test the API endpoints (e.g., `POST /api/launch`) and assembled services.
    *   **E2E (Critical Paths):** Test the full flow only for critical user journeys.

*   **Mocking Principle: "Mock at the System Boundary Only"**
    *   **Integration Tests:** Do **not** mock the Service layer. Do **not** mock internal resources that can be easily instantiated (like the Filesystem).
        *   **Good:** Use `tmp_path` to create real files, then call the API. This verifies the full stack: `HTTP -> Router -> Service -> Real FS`.
        *   **Bad:** Mocking `os.listdir` in an API test. This degrades the test to a slow unit test.
    *   **When to Mock:** Only mock **slow, dangerous, or non-deterministic** external boundaries.
        *   **Allowed Mocks:** `subprocess.run` (don't actually run Docker), `requests.get` (don't hit real URLs), `time.sleep`.
        *   **Forbidden Mocks:** `FileSystemService`, `os.path` (use `tmp_path`), internal helper classes.
    *   **Goal:** Execute the code path through the full application stack and only fake the final "impossible" system call.

*   **Target Distribution:**
    *   **Integration:** ~80% of your effort. This gives the highest confidence per minute spent.
    *   **Unit:** ~10%. Only for logic that is too complex to test via the API or has too many permutations.
    *   **E2E:** ~10%. Only for "smoke testing" the critical paths.

    *   **Guideline:** "Prioritize Integration Tests for API Endpoints." Tests that verify the *behavior* of the API (input -> output) are more resilient to refactoring than unit tests that verify the *implementation details* of a service.



### 5.7 File System Testing

*   **No Mocks for Filesystem:** Do **not** mock `os.listdir`, `os.path.exists`, `open()`, or `glob` when testing file system operations.

    *   **Why:** Mocking the file system often leads to "tautological" tests that verify the mock configuration rather than the code's behavior. It also makes tests brittle to implementation changes (e.g., switching from `os.path` to `pathlib`).

*   **Use `tmp_path`:** Use the standard `pytest` fixture `tmp_path` to create real, temporary directory structures for each test.

    *   **Pattern:**

        ```python

        def test_list_files(tmp_path):

            # Setup: Create real files in the temp dir

            (tmp_path / "file1.txt").touch()

            (tmp_path / "subdir").mkdir()

            

            # Action: Call the function with the temp path

            result = my_file_service.list_files(str(tmp_path))

            

            # Assert: Verify the result

            assert "file1.txt" in result

        ```


