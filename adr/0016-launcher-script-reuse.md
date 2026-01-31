# 4. Hub Launcher via Script Reuse

Date: 2026-01-25

## Status

Accepted (Refines [ADR-0003](./0003-launcher-path-mirroring.md))

## Context

In [ADR-0003](./0003-launcher-path-mirroring.md), we decided to enable the Hub to launch new sessions. We chose to **reuse the `gemini-toolbox` script** rather than reimplementing logic in Python.

We also identified a need for a seamless "Launch Remote, Continue Local" workflow. A user might start a session from their phone via the Hub, but later want to switch to their desktop terminal to continue working in the same session without restarting.

## Decision

We will bundle the `gemini-toolbox` script into the Hub container at **build time** and enhance it to support detached sessions and re-attachment.

### 1. Build-Time Copy
We copy `bin/gemini-toolbox` into the `images/gemini-hub/` context and bake it into the image.

### 2. Environment Mirroring
To make the script believe it is running on the Host, we mirror the relevant environment at runtime:
*   **Workspace:** Mirror mounted (as per ADR-0003).
*   **Home Directory:** We set `HOME` inside the Hub to match the Host's `HOME`.

### 3. Execution Flow (Launch)
1.  User clicks "Launch" in Hub UI.
2.  Hub Python Backend calls `subprocess.run(["gemini-toolbox", "--detached", ...], env={"HOME": host_home})`.
    *   The `--detached` flag tells the script to start the container and the internal `tmux` session but **skip** the final `docker attach` step.
3.  The script (running inside container) sends the `docker run` command to the Host Daemon.
4.  The session starts in the background on the Host.

### 4. Execution Flow (Connect)
To allow the user to pick up the session on the desktop:
1.  We implement a `connect` command in `gemini-toolbox`.
2.  User runs `gemini-toolbox connect <SESSION_ID>`.
3.  The script executes `docker exec -it <SESSION_ID> gosu gemini tmux attach -t gemini`.
4.  The user is instantly connected to the active session.

## Consequences

### Positive
*   **Reliability:** The script is baked into the image.
*   **Continuity:** Sessions are persistent and device-agnostic. You can start on mobile and finish on desktop.
*   **DRY:** Single source of truth for session startup logic.

### Negative
*   **Rebuild Requirement:** Updating the script requires rebuilding the Hub.