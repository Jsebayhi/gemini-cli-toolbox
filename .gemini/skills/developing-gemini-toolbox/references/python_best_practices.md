# Python Engineering Standards

These standards ensure that all Python components within the Gemini CLI Toolbox remain maintainable, type-safe, and production-ready.

## 1. Type Safety
- **Mandatory Hinting:** All function signatures must include type hints for parameters and return values.
- **Generic Support:** Use `from typing import ...` for complex types (List, Dict, Generator).
- **Static Analysis:** Code must pass `ruff` linting and follow PEP 8 style guidelines.

## 2. Dependency Management
- **Scoping Pattern:** Use split requirements files to prevent production bloat.
    - `requirements.txt`: Production-only dependencies (e.g., Flask, Gunicorn).
    - `requirements-test.txt`: Testing and development tools (e.g., Pytest, Playwright, Xdist).
- **Pinning:** All dependencies MUST be pinned to a specific version (e.g., `flask==3.0.0`).
- **Inheritance:** `requirements-test.txt` should implicitly or explicitly include production dependencies.

## 3. Global State & Thread Safety
- **No Direct Mutation:** NEVER modify global class attributes or module-level variables directly in tests.
- **Monkeypatching:** Use the `monkeypatch` fixture to safely override configuration or environment variables for the duration of a single test.
- **Parallel Readiness:** Assume tests will run in parallel (via `pytest-xdist`). Ensure every test is isolated and does not rely on shared mutable state.

## 4. Log Hygiene
- **Green Logs Policy:** CI output should be clean. Do not allow tests to produce noisy `ERROR` or `WARNING` logs if the failure is expected.
- **Suppression Fixtures:** Use a `suppress_logs` fixture (setting logger levels to `CRITICAL`) when testing "sad paths" that would otherwise pollute the output.

## 5. Architectural Patterns
- **App Factory:** Use the Application Factory pattern for Flask/Web services to enable easy testing and prevent circular imports.
- **Service Layer:** Keep business logic in pure Python modules (`app/services/`) that do not depend on the web framework.
