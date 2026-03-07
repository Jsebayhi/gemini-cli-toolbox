# ADR-0058: Transitioning to Rate-Limited External Auto-Update

Date: 2026-03-07

## Status

Accepted

## Context

ADR-0055 enabled internal auto-update for the `gemini-cli` by granting write access to the global NPM prefix. However, since the toolbox primarily uses ephemeral containers (`--rm`), any updates applied inside the container are lost once it terminates.

Furthermore, automatic checks for updates from within the CLI can introduce latency and unintended network traffic.

## Decision

We will shift the responsibility of auto-updating to the host-side `gemini-toolbox` script. The script will perform a `docker pull` for remote images to ensure the latest version is available before launch.

To prevent excessive network traffic and startup latency, this check will be rate-limited to at most once per hour.

**Implementation Details:**
1.  **Rate-Limiting:** A timestamp file will be stored in the cache directory (`${XDG_CACHE_HOME:-$HOME/.cache}/gemini-toolbox/last-update-check`).
2.  **Pull Logic:** If the image is a remote image with a `latest` tag, and the last check was more than 3600 seconds ago, the script will attempt a `docker pull`.
3.  **Read-Only CLI:** The `$NPM_CONFIG_PREFIX` in the `gemini-cli` image will be set back to read-only (`755`) for the `gemini` user to prevent inconsistent internal updates.

## Consequences

### Positive
*   **Persistence:** Updates are now pulled as new Docker images, which are persistent on the host.
*   **Performance:** Rate-limiting ensures that most runs are near-instant, with update checks happening only once an hour.
*   **Consistency:** All sessions for a given project will use the same image version until the next hourly check.

### Negative
*   **First Run Latency:** The very first run of the day (or hour) may be slightly slower if a pull is triggered.
*   **Cache File Dependency:** Requires the presence of a writable cache directory on the host.
