# ADR 0037: Automated UI Testing with Playwright

## Status
Accepted

## Context
The Gemini Hub UI currently lacks automated end-to-end (E2E) testing. This increases the risk of regressions during UI development and slows down the validation of new features. We need a robust, modern UI testing framework that integrates well with our existing Python-based testing infrastructure (`pytest`).

## Alternatives Considered

### 1. Playwright Python with Pytest (Selected)
Use `playwright-python` and the `pytest-playwright` plugin to write UI tests in Python.
*   **Pros:**
    *   Seamless integration with existing `pytest` infrastructure and fixtures.
    *   Adheres to `ENGINEERING_STANDARDS.md` (Testing Trophy) by keeping E2E tests alongside unit/integration tests.
    *   Single language (Python) for all testing logic.
    *   Playwright's modern features (auto-waiting, tracing, codegen).
*   **Cons:**
    *   Increases test Docker image size due to browser binaries.

### 2. Dedicated Node.js Playwright Container
Create a separate `images/gemini-hub-ui-tests` directory with a Node.js environment and standard Playwright (JS/TS).
*   **Pros:**
    *   Uses the most mature and widely-used version of Playwright.
*   **Cons:**
    *   Adds architectural complexity (requires multi-container orchestration for tests).
    *   Introduces Node.js dependency to a Python-centric component.
*   **Reason for Rejection:** The complexity of managing a separate Node.js environment and orchestrating multiple containers for simple smoke tests outweighs the benefits of the native JS/TS environment.

### 3. Selenium with Python
Use the traditional Selenium WebDriver for Python.
*   **Pros:**
    *   Very well-established and widely understood.
*   **Cons:**
    *   Slower execution compared to Playwright.
    *   More brittle tests due to lack of built-in auto-waiting.
    *   More manual configuration required for browser drivers.
*   **Reason for Rejection:** Playwright provides a significantly better developer experience and faster execution times, which is critical for maintaining a rapid development cycle.

## Decision
We will implement automated UI tests using **Playwright Python** integrated with **pytest**. 

## Consequences
*   We will add `pytest-playwright` to our test dependencies.
*   The `images/gemini-hub/tests/Dockerfile` will be updated to install Playwright and its required browser binaries (specifically Chromium for smoke tests).
*   UI tests will be located in `images/gemini-hub/tests/ui/`.
*   The `Makefile` will be updated to support running UI tests.
*   Test execution time will increase slightly, but confidence in UI stability will significantly improve.
