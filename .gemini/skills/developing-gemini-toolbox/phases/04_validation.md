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
