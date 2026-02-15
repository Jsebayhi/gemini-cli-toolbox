# Python UI Testing Implementation (Playwright)

Specific standards for testing web UIs using the Playwright-Python toolchain.

## 1. Tooling
- **Framework:** `playwright-python` with the `pytest-playwright` plugin.
- **Async Handling:** Prefer the synchronous API (`playwright.sync_api`) for test simplicity unless high concurrency is required within a single test.

## 2. Process Isolation for Mocks
- **The Process Limit:** Python mocks are memory-local.
- **The Requirement:** The live HTTP server MUST run in the same process memory as the test runner.
- **Implementation:** Use a manual `threading` server in `conftest.py` using `werkzeug.serving.make_server`. DO NOT use external process runners like `pytest-flask` if you rely on `unittest.mock`.

## 3. Selector Standards
- **Scoped Locators:** Use `page.locator("#container").get_by_text(...)` to ensure locators are resilient to changes outside the target component.
- **Auto-waiting Assertions:** Use `expect(locator).to_have_text(...)` instead of manual boolean checks to leverage Playwright's automatic polling.

## 4. Failure Observability
- **Trace Integration:** Implement a `_auto_tracing` fixture in `conftest.py`.
- **Logic:**
    - Call `context.tracing.start` before UI tests.
    - Save to `test-results/trace-{test_name}.zip` ONLY if `request.node.rep_call.failed` is true.
    - This allows devs to view the full execution lifecycle in the Playwright Trace Viewer.

## 5. Clean State
- **Browser Contexts:** The `page` fixture is fresh, but explicitly clear `localStorage` via `page.evaluate` if testing persistence features like "Recent Paths."
