# 7. VS Code Integration Strategy

Date: 2026-01-08

## Status

Accepted

## Context

We want to use the `@google/gemini-cli` inside a Docker container while interacting with the VS Code instance running on the Host OS. This provides a "best of both worlds" experience: the isolation and standardized environment of Docker, combined with the rich UI of the host's IDE.

The integration faced three major blocking issues:
1.  **Environment Stripping:** Docker strips host environment variables (`GEMINI_CLI_IDE_*`) needed for authentication.
2.  **Path Mismatch:** The CLI enforces a security check where the container's `PWD` must match the Host's Workspace Path.
3.  **Network/Host Mismatch (Critical):** The Gemini CLI, upon detecting it is running inside a container (`/.dockerenv`), **hardcodes** the target hostname to `host.docker.internal`.
    *   **The Problem:** The VS Code Companion Extension listens on `127.0.0.1` (localhost) for security. It *rejects* connections addressed to `host.docker.internal` (which resolves to the Docker Gateway IP, e.g., `172.17.0.1`) with a `403 Forbidden` or connection failure.
    *   **The Constraint:** We use `--net=host` to allow the container to access the host's loopback interface easily, but we cannot easily force the CLI to use `127.0.0.1` because of the hardcoded logic.

## Decision

We have implemented a robust solution involving a **Source Code Patch** during the Docker build.

### 1. Build-Time Patching (The Core Fix)
*   **Action:** We modify the installed `@google/gemini-cli-core` source code using `sed` in the `Dockerfile`.
*   **The Change:** We use a resilient "Smart Patch" that detects the code pattern (legacy line-based or new function-based) and injects a check for `GEMINI_CLI_IDE_SERVER_HOST`.
*   **Logic (Legacy):**
    ```javascript
    // Original
    return isInContainer ? 'host.docker.internal' : '127.0.0.1';

    // Patched
    return process.env.GEMINI_CLI_IDE_SERVER_HOST || (isInContainer ? 'host.docker.internal' : '127.0.0.1');
    ```
*   **Logic (Modern):**
    ```javascript
    // Original
    export function getIdeServerHost() {

    // Patched
    export function getIdeServerHost() { if (process.env.GEMINI_CLI_IDE_SERVER_HOST) return process.env.GEMINI_CLI_IDE_SERVER_HOST;
    ```
*   **Result:** This allows us to override the hardcoded behavior across different CLI versions without forking the entire project.

### 2. Wrapper Configuration (`bin/gemini-toolbox`)
*   **Network:** Uses `--net=host`.
*   **Environment Variable Management (Conditional):**
    *   **Auto-Detection:** The script checks `TERM_PROGRAM` to detect if it is running inside a VS Code terminal.
    *   **Integration Enabled:** If VS Code is detected (and not explicitly disabled), the script:
        *   Sets `GEMINI_CLI_IDE_SERVER_HOST=127.0.0.1` to trigger our patch.
        *   Passes `TERM_PROGRAM` to enable the feature in the CLI.
        *   Passes `GEMINI_CLI_IDE_*` variables (Port, Token, Workspace) captured from the host environment.
    *   **Integration Disabled:** If VS Code is NOT detected, or if the user passes `--no-ide`:
        *   **None** of the above variables are passed to the container.
        *   This ensures the CLI runs in "clean" mode (Standard Terminal) and does not attempt to connect to a non-existent IDE server.
*   **Filesystem:** Mirrors the host's project directory structure inside the container (e.g., `/home/user/project` -> `/home/user/project`) to satisfy the workspace path security check.

## Consequences

### Positive
*   **Robustness:** No DNS spoofing (`/etc/hosts`) or complex socket mounting is required.
*   **Simplicity:** The runtime configuration is minimal and clean.
*   **Performance:** Direct TCP connection to `127.0.0.1` is fast and standard.
*   **Flexibility:** Users can opt-out via `--no-ide` if they encounter issues or prefer a disconnected session.

### Negative
*   **Maintenance:** The `sed` patch in the Dockerfile is brittle. If Google changes the internal structure of `ide-client.js` (e.g., variable names or file paths), the build will break or the patch will silently fail (though `sed` usually fails on no match).
*   **Action:** We must verify the patch application during upgrades.
