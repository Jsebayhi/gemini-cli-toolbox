# Python Engineering Standards

These standards ensure that all Python components within the Gemini CLI Toolbox remain maintainable, type-safe, and production-ready.

## 1. Type Safety
- **Mandatory Hinting:** All function signatures must include type hints for parameters and return values.
- **Generic Support:** Use `from typing import ...` for complex types (List, Dict, Generator).
- **Static Analysis:** Code must pass `ruff` linting and follow PEP 8 style guidelines.

## 2. Dependency Management
- **Scoping Pattern:** Use split requirements files to prevent production bloat.
    - `requirements.txt`: Production-only dependencies (e.g., Flask, Gunicorn).
    - `requirements-test.txt`: Testing and development tools.
- **Pinning:** All dependencies MUST be pinned to a specific version (e.g., `flask==3.0.0`).

## 3. Architectural Patterns
- **App Factory:** Use the Application Factory pattern for Flask/Web services to enable easy testing and prevent circular imports.
- **Service Layer:** Keep business logic in pure Python modules (`app/services/`) that do not depend on the web framework.
- **Subprocess Safety:** Always use list-based arguments `["cmd", "arg"]` instead of `shell=True` to prevent injection.
- **Centralized Config:** Use a central `Config` class to load and validate environment variables at startup. Fail fast if required variables are missing.
