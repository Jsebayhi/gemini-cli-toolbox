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

*   **Unit Tests:** Focus on `app/services/`. These should run fast and mock external calls (like `subprocess`).
*   **Integration Tests:** Use `pytest-flask` to test API endpoints (`/api/...`) against a test app instance.
