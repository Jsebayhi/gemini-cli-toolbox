# ADR-0053: Fail-Fast Permission Strategy

## Status
Accepted

## Date
2026-02-26

## Context
Previous ADR (ADR-0003) established a strategy where the container entrypoint would automatically fix ownership of the home directory using `chown -R`. This was intended to provide a "Zero-Config" experience.

However, automatically modifying host file permissions can be unexpected and intrusive for users. Furthermore, since we already create the container user with a UID/GID matching the host user, permissions should naturally match in most cases unless the host environment is misconfigured or a volume was previously used by a different user.

## Decision
We will shift from an **Automatic Fix** to a **Fail-Fast** permission strategy.

1.  The entrypoint will **no longer** perform recursive `chown -R` on the home directory.
2.  The entrypoint will **verify** that the home directory (`$HOME`) is owned by the target UID/GID.
3.  If a mismatch is detected, the entrypoint will **fail clearly** with an error message explaining the situation and providing the exact command the user should run on their host to fix it.

## Alternatives Analyzed

### 1. Automatic Fix (ADR-0003)
*   **Description:** Automatically fix permissions on startup.
*   **Pros:** High UX (automatic fix).
*   **Cons:** Intrusive; modifies host files without explicit user consent. Slow on large volumes.
*   **Status:** Superseded by this ADR.

### 2. Warn-only (Non-Blocking)
*   **Description:** Log a warning if permissions mismatch but proceed anyway.
*   **Pros:** Never blocks startup.
*   **Cons:** Leads to cryptic "Permission Denied" errors later when the Agent tries to write logs, history, or code, which is harder to diagnose than a startup failure.
*   **Status:** Rejected.

### 3. Fail-Fast (Blocking)
*   **Description:** Detect mismatch and exit immediately with a helpful error.
*   **Pros:** Explicit, safe, and transparent. Does not modify host files.
*   **Cons:** Requires manual user intervention if permissions are wrong.
*   **Status:** Selected.

## Consequences
*   **Security:** Improved transparency; the container never modifies host file ownership.
*   **UX:** Users might need to run a manual `chown` command if they move their configuration or change their UID.
*   **Maintenance:** Simplifies the entrypoint logic by removing the recursive traversal entirely.
