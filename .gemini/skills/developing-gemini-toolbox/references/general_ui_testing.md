# General UI Testing Standards

These standards define the architectural approach for testing web and mobile interfaces within the Gemini Toolbox.

## 1. Page Object Model (POM) & Composition
- **Decoupling:** Test files should contain user intent; Page Objects should contain implementation details.
- **Component Composition:** Avoid "God Objects." Split the POM into modular, nested components for scalability.

## 2. Deterministic Interactivity
- **Signal-Based Waiting:** NEVER use static timers. 
- **Wait for State:** Wait for specific UI state changes (visibility, text, counts) to ensure tests are fast and robust.

## 3. Observability & Zero-Noise Policy
- **Rich Artifacts:** Automatic failure tracing (screenshots, logs).
- **Zero-Console-Error:** UI tests MUST fail if unexpected errors are detected in the browser console, even if all assertions pass. This catches silent regressions and maintains high code quality.

## 4. State Management & Navigation
- **Persistence Reset:** Explicitly clear client-side storage between tests.
- **Stable Entry Points:** Every test should start from a known stable URL to prevent cascading failures.
