# General UI Testing Standards

These standards define the architectural approach for testing web and mobile interfaces within the Gemini Toolbox.

## 1. Page Object Model (POM)
- **Concept:** Encapsulate UI implementation details (selectors, interaction logic) into high-level Page Objects.
- **Rule:** Test files should contain "What" (user intent), Page Objects should contain "How" (implementation).
- **Benefit:** If the UI layout changes, you only update one Page Object instead of dozens of tests.

## 2. Deterministic Interactivity
- **Signal-Based Waiting:** NEVER use static timers (e.g., `sleep(500ms)`). 
- **Wait for State:** Always wait for a specific UI state change (e.g., element visibility, text change, count update) before proceeding.
- **Strict Mode:** If a selector matches multiple elements, the test is ambiguous and should fail.

## 3. Observability
- **Rich Artifacts:** In headless/CI environments, tests must produce visual proof of failure.
- **Tracing:** Capture screenshots, console logs, and network snapshots automatically upon failure.

## 4. State Management
- **Persistence Reset:** Explicitly clear browser-side storage (localStorage, Cookies) between tests to ensure isolation.
- **Navigation:** Every test should ideally start from a known entry point (e.g., the dashboard) to prevent cascading failures.
