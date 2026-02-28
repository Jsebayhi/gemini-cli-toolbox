# Phase 4: Validation

**Goal:** Ensure the changes are safe, correct, and compliant.
**Rule:** You are **forbidden** from pushing without validation.

## 1. Local CI (Mandatory)
Run the full local suite:
```bash
make local-ci
```
*   **Includes:** Bash Linting (ShellCheck), Python Linting (Ruff), Unit Tests (Pytest).
*   **On Failure:** Fix the issue. Do not suppress it without a documented reason.

## 2. Security Scan
Check for new vulnerabilities:
```bash
make scan
```
*   **Policy:** The release pipeline MUST be zero-vulnerability (CRITICAL/HIGH).
*   **Suppression:** If you must suppress a CVE in `.trivyignore`, you MUST follow the [DevSecOps Governance](../references/devsecops.md) (Individual entries + 90-day TTL).
*   **Ownership:** Verify that any new vulnerabilities aren't introduced by your direct dependencies.

## 3. Manual Verification
*   Execute the relevant **User Journey** from `docs/internal/MAINTENANCE_JOURNEYS.md`.
*   If a new feature, add a new Journey (See Phase 2).

## 4. Cleanup & Simplification (Mandatory)
Once you have verified your work and ensured all tests pass, you MUST perform a final cleanup of your code.
- **Identify Unneeded Changes:** Review your git diff and revert any changes that were part of your research or experimentation but are not necessary for the final solution.
- **Simplify Logic:** Look for opportunities to simplify complex logic that you've implemented now that you have a complete picture of the solution.
- **Remove Debug Prints:** Ensure all debug logs, print statements, or temporary test code are removed.
- **Why:** This ensures the final Pull Request is focused, high-quality, and easy to review.
