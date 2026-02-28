# ADR-0056: Robust Docker GID Detection

**Date:** 2026-02-28
**Status:** Accepted

## Context
The Gemini CLI toolbox relies on Docker-out-of-Docker (DooD) to allow the AI agent to orchestrate the host's Docker daemon. This requires passing the host's Docker socket Group ID (GID) to the container via the `HOST_DOCKER_GID` environment variable.

Previously, both `gemini-toolbox` and `gemini-hub` scripts relied on `getent group docker` to detect this GID. This approach had several limitations:
1.  **Group Name Dependency:** It assumes the group is named exactly "docker" on the host.
2.  **Shadowing in Containers:** When `gemini-toolbox` is run inside another container (like the Hub), it re-detects the GID. If the Hub container lacks a "docker" group, the GID is lost and set to empty, even if it was correctly passed by the host to the Hub.
3.  **Command Availability:** Some minimal environments might not have the `getent` command.

## Decision
We will upgrade the `HOST_DOCKER_GID` detection logic in `gemini-toolbox` and `gemini-hub` to be more robust:
1.  **Respect Environment:** The scripts will now respect `HOST_DOCKER_GID` if it's already set in the environment (e.g. passed from host to Hub).
2.  **Primary Detection via Socket:** If not set, the scripts will try to detect the GID directly from the `/var/run/docker.sock` file using `stat -c %g`.
3.  **Fallback to Group Lookup:** If `stat` is unavailable or fails, it will fall back to `getent group docker` for compatibility.

## Rationale
*   **Chain of Custody:** By respecting the environment variable, we ensure that a GID correctly detected on the host is preserved throughout the session lifecycle (Host -> Hub -> Agent Cli).
*   **Empirical Discovery:** Using `stat` on the socket is the most reliable way to find the GID that actually controls access to the daemon, regardless of what the group is named or if it's even defined in `/etc/group` (as is common in some containerized environments).
*   **Backward Compatibility:** Falling back to `getent` ensures that the script continues to work on systems where the socket might not be at the standard path during detection but the group exists.

## Consequences
*   **Improved Reliability:** DooD now works reliably even when starting sessions from the Gemini Hub dashboard.
*   **Tool Requirement:** The scripts now have a soft dependency on `stat` (standard in `coreutils`). Since the toolbox is designed for Linux-based environments (or WSL), this is acceptable.
