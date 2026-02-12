# Phase 3: Validation

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
*   **Policy:** If a new vulnerability appears, verify if it's caused by your changes. If so, fix it unless it is just a question of waiting for an upstream patch.

## 3. Manual Verification
*   Execute the relevant **User Journey** from `docs/internal/MAINTENANCE_JOURNEYS.md`.
*   If a new feature, add a new Journey (See Phase 2).
