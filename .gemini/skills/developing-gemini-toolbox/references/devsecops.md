# DevSecOps & Security Governance

This document defines the mandatory security practices and risk governance models for the Gemini CLI Toolbox.

## 1. The "Shift Left" Mandate
Security is not a final step; it is an integrated part of development.
*   **Local Scans:** You MUST run `make scan` locally before opening a PR.
*   **Component Ownership:** Every component Makefile MUST implement a `scan` target that targets its specific image tag and respects the root `.trivyignore`.

## 2. Vulnerability Management (.trivyignore)
Suppressing a vulnerability is a **governed risk decision**, not a shortcut.

### 2.1 The TTL Policy (Time-To-Live)
Every entry in the project-wide `.trivyignore` MUST be auditable.
*   **Per-CVE Governance:** Each CVE must be listed individually.
*   **Expiration Date:** Every entry MUST include a `# Review Required By: YYYY-MM-DD` comment.
*   **Cycle:** Use a **90-day** review cycle from the date of detection/suppression.

### 2.2 Justification Requirements
A suppression is only valid if it meets one of these criteria:
1.  **Unfixable Upstream:** No fixed version exists, and the vulnerability is in a third-party dependency (e.g., `stdlib`, `npm` sub-dependency).
2.  **Zero-Risk Context:** The vulnerability exists but is not exploitable in our specific environment (e.g., a DoS in a local dev tool that doesn't expose a public network service).
3.  **OS-Level Delay:** A fix exists but hasn't been backported to the base image's OS release (e.g., Debian Bookworm).

## 3. Transparency & Documentation
*   **Risk Acceptance:** Significant risk acceptances (like CRITICAL vulnerabilities) MUST be documented in `docs/ARCHITECTURE_AND_FEATURES.md`.
*   **Contributing:** All contributors MUST be informed of this policy in `docs/CONTRIBUTING.md`.

## 4. CI/CD Integration
*   **Delegation:** The GitHub Action MUST delegate scanning to the `make scan` target of each component. Do not use hardcoded Trivy actions with separate logic.
*   **Failure Policy:** CI MUST fail on any **CRITICAL** or **HIGH** severity vulnerability that is not explicitly suppressed with a valid TTL.
