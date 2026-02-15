# General Testing Standards (Language Agnostic)

These principles apply to all components in the Gemini CLI Toolbox, regardless of the implementation language.

## 1. The Testing Trophy
We prioritize tests that provide the highest confidence-to-cost ratio.
- **Static Analysis:** Use linters and type checkers to catch syntax and basic logic errors early.
- **Unit Tests:** Focus on complex, isolated algorithmic logic. Keep them fast and pure.
- **Integration Tests:** The bulk of the suite. Verify that components work together and correctly interface with system boundaries.
- **E2E Smoke Tests:** Verify critical user journeys from end to end.

## 2. Mocking Philosophy
- **Mock at the Boundary:** Only mock slow, non-deterministic, or dangerous external systems (Network, Time, Subprocesses).
- **Favor Realism:** Do not mock internal services or helper classes. If a component can be instantiated easily, use the real implementation.
- **Data over Mocks:** Use real files or temporary database instances instead of mocking filesystem APIs or database queries whenever possible.

## 3. Test Qualities
- **Atomicity:** Each test should verify a single logical outcome.
- **Isolation:** Tests must be independent. The success or failure of one test must not affect another.
- **Determinism:** Tests must produce the same result every time. Avoid static delays; wait for signals.
- **Clean Slate:** Every test must start with a fresh environment (namespaces, temporary directories, etc.).
