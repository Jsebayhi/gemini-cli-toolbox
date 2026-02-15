# Python UI Testing Implementation (Playwright)

Specific standards for testing web UIs using the Playwright-Python toolchain.

## 1. Tooling & Resilience
- **Framework:** `playwright-python` with the `pytest-playwright` plugin.
- **Async Handling:** Prefer the synchronous API (`playwright.sync_api`) for test simplicity.
- **Retries:** Use `pytest-rerunfailures` (e.g., `--reruns 1`) in CI to mitigate non-deterministic browser flakiness.

## 2. Page Object Model (POM) & Composition
- **Composition over God Objects:** Split the POM into logical components. For example, a `HubPage` should contain a nested `LaunchWizard` instance.
- **Interface:** Tests interact via these components: `hub.wizard.launch()`. This keeps the main Page Object clean and maintainable.

## 3. Process Isolation for Mocks
- **The Requirement:** The live HTTP server MUST run in the same process memory as the test runner.
- **Implementation:** Use a manual `threading` server in `conftest.py` using `werkzeug.serving.make_server`. 

## 4. Selector Standards & Semantic Assertions
- **Scoped Locators:** Use `page.locator("#container").get_by_text(...)`.
- **Semantic Helpers:** Add domain-specific assertion methods to the POM (e.g., `hub.expect_inactive_session("proj1")`) instead of checking specific CSS properties like `opacity` directly in the test.

## 5. Failure Observability
- **Trace Integration:** Implement an `_auto_tracing` fixture in `conftest.py`.
- **Logic:** Save to `test-results/trace-{test_name}.zip` ONLY if the test fails. This provides snapshots, console logs, and network activity for debugging.

## 6. Clean State
- **Browser Contexts:** Clear `localStorage` via `page.evaluate` if testing persistence features. Ensure every test starts from a clean client-side state.
