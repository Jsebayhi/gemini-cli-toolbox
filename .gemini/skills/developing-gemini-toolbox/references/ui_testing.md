# UI Testing Best Practices (Playwright)

Our UI tests prioritize determinism, maintainability, and rapid debugging through failure tracing.

## 1. Page Object Model (POM)
- **Decoupling:** NEVER hardcode DOM selectors or implementation details (IDs, classes) directly in the test file.
- **Pattern:** Create a `pages.py` file containing high-level classes (e.g., `HubPage`) that encapsulate interactions and locators.
- **Readability:** Tests should read like user stories: `hub.open_wizard()`, `hub.launch_task("hello")`.

## 2. Deterministic Waiting
- **No Static Sleeps:** NEVER use `wait_for_timeout(ms)`. This leads to flaky tests.
- **Signal-Based waiting:** Use Playwright's `expect` assertions. They poll the UI and continue the instant the condition is met (e.g., `expect(locator).to_have_text(...)`).

## 3. Selector Robustness
- **Scoped Locators:** Avoid global text searches that might match multiple elements (Breadcrumbs vs. List Items). 
- **Pattern:** Always scope locators to a container: `page.locator("#roots-list").get_by_text(...)`.
- **Strict Mode:** Adhere to Playwright's strict mode; if a selector matches two elements, it is a bug in the test.

## 4. Process Isolation for Mocks
- **Unified Memory Space:** When mocking Python services (using `patch`) for UI tests, the live web server MUST run in the same process as the test runner.
- **Implementation:** Use a manual `threading` server in `conftest.py` rather than an external process runner.

## 5. Observability (Failure Tracing)
- **Automatic Traces:** Every UI test run in CI should automatically start tracing.
- **Artifacts:** Traces (screenshots, snapshots, console logs) must be saved only on failure to `test-results/*.zip` for immediate debugging.

## 6. State Isolation
- **Client-Side Cleansing:** Explicitly clear `localStorage`, `sessionStorage`, and `cookies` at the start or end of tests that modify client state to prevent leakage.
