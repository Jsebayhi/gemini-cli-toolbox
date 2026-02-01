# ADR 0020: Hub Session Execution and Architecture

## Status
Accepted

## Context
The Gemini Hub allows users to launch CLI sessions from a web interface. During implementation, several critical issues were encountered regarding permissions, session types, and terminal rendering. This ADR documents the solutions to ensure robust operation.

## Decisions

### 1. Permission Management (The "Root" Issue)
**Problem:** The Hub runs as `root` (inside its container) to access the host Docker socket (DooD). When it launched a session container, `gemini-toolbox` detected `UID=0` and launched the session as `root`, causing the session entrypoint to `chown` host-mounted volumes to `root`, corrupting file permissions on the host.

**Solution:**
*   The Hub launcher (`bin/gemini-hub`) now captures the host user's UID/GID and passes them as `HOST_UID` / `HOST_GID` environment variables to the Hub container.
*   `gemini-toolbox` checks for these variables. If present (indicating execution from Hub), it uses them instead of `$(id -u)`.
*   This ensures the session container always runs as the correct host user (e.g., 1000), regardless of the caller's identity.

### 2. Docker Socket Access (HOST_DOCKER_GID)
**Problem:** When `gemini-toolbox` runs inside the Hub container (to launch a session), it attempts to detect the `docker` group GID to grant the session user access to the socket. However, it detects the GID from the *Hub container's* `/etc/group` (e.g., 999), which rarely matches the Host's Docker GID (e.g., 135). This results in "Permission Denied" when the session user tries to use `docker`.

**Solution:**
*   **Host Wrapper (`bin/gemini-hub`):** Detects the *Host's* `docker` group GID (`HOST_DOCKER_GID`) and passes it as an environment variable to the Hub container.
*   **Toolbox Script (`bin/gemini-toolbox`):** When running inside the Hub (or anywhere), it checks if `HOST_DOCKER_GID` is already set in the environment. If set, it uses that value instead of attempting auto-detection.
*   **Result:** The session container receives the correct Host GID, creates the corresponding group, and the user gains valid access to the mapped socket.

### 3. Detached Bash Sessions
**Problem:** Launching a "Bash Shell" session in detached mode caused the container to exit immediately because `bash` requires a TTY or input stream to stay alive. Running `sleep infinity` kept it alive but broke `ttyd` (which attaches to `tmux`) because `tmux` wasn't running.

**Solution:**
*   **Toolbox:** `gemini-toolbox` passes `bash` as the command, even in detached mode.
*   **Entrypoint:** `docker-entrypoint.sh` detects detached mode (no TTY). Instead of attempting `tmux attach` (which fails without TTY), it enters a wait loop: `while tmux has-session ...; do sleep 1; done`.
*   **Tmux:** Keeps `bash` running in the background.
*   **Result:** The container stays alive, and `ttyd` can successfully attach to the active `tmux` session, providing a fully functional web-based shell.

### 3. Terminal Rendering
**Problem:** Sessions launched from the Hub sometimes showed "weird colors" or ignored input.
**Cause:** The Hub service environment often lacks a `TERM` variable, passing `TERM=dumb` or empty to the session. `tmux` disables advanced features in this state.
**Solution:** `gemini-toolbox` enforces `TERM=xterm-256color` if the environment provides a deficient value.

### 4. Session Capabilities (CLI vs Bash)
**Decision:** The Hub Wizard offers an explicit choice between:
*   **Gemini CLI:** The standard AI chat interface.
*   **Bash Shell:** A raw shell environment. This is a first-class feature enabling remote work (e.g., editing files with `vim`, running git commands manually) from any browser, effectively turning the Hub into a lightweight remote workspace.

## Consequences
*   **Reliability:** File permissions on the host are protected.
*   **Utility:** Users can perform complex terminal tasks remotely without needing SSH setup.
*   **Consistency:** The container environment behaves identically whether launched locally or via the Hub.
