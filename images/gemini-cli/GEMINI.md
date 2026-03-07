# Component Context: Gemini CLI

This document provides operational context for AI agents working specifically on the `gemini-cli` container.

## 1. Component Overview
A Debian-based Docker image wrapping the `@google/gemini-cli`. It focuses on seamless host integration (permissions, networking, volumes).

## 2. File Map (Component Level)

| File | Purpose |
| :--- | :--- |
| `Dockerfile` | **The Environment.** Node.js 20 (Bookworm), `gosu`, and the CLI tool. |
| `docker-entrypoint.sh` | **The Logic.** Runtime script that fixes permissions and switches user via `gosu`. |
| `Makefile` | **The Builder.** Local build commands (`build`, `rebuild`) for this image. |
| `adr/` | **The Decisions.** Records explaining Debian vs Alpine, `gosu` usage, etc. |

## 3. Operational Workflows

### Building (Local)
Run from `images/gemini-cli/`:
```bash
make build
# or
make rebuild
```

### Debugging
To inspect the container internals:
```bash
# Run the wrapper with debug flag (from project root)
bin/gemini-toolbox --debug
```

## 4. Known Peculiarities & Gotchas

### Remote Access Behavior
*   **Scrolling:** The entrypoint automatically generates a `~/.tmux.conf` with `mouse on` if one is missing. This enables scrolling in the web terminal (ttyd).
*   **Session:** Remote access forces the session into `tmux`.

### The "Input Lag" Issue
*   **Symptom:** Severe latency when typing in the interactive chat.
*   **Cause:** Large host configuration folder (`~/.gemini`) causing slow synchronous I/O.
*   **Fix:** Clean the host configuration folder.

### Permission Architecture
*   **Concept:** The container starts as `root`, creates a user matching `DEFAULT_UID` (from host), and drops privileges via `gosu`.
*   **Fail-Fast Permission Strategy (ADR-0053):** To ensure safety and performance, the entrypoint **never** performs recursive `chown -R` on the home directory. Instead, it verifies that the home directory ownership matches the target UID/GID and fails immediately with troubleshooting instructions if a mismatch is detected.
*   **Surgical Parent Fix (ADR-0057):** When Docker creates missing parent directories for volume mounts (e.g., `/home/gemini/.config`), they are owned by `root`. The entrypoint automatically performs a surgical, non-recursive `chown` on any root-owned sub-items in `/home/gemini` that are NOT mount points. It uses `find -xdev` to ensure it never traverses into large host-mounted volumes, preserving performance.
*   **Immutability (ADR-0058):** The global NPM prefix (`/opt/npm-global`) is read-only for the `gemini` user. Auto-updates are handled by the host-side launcher via image pulls.
*   **Rule:** Never remove `gosu` or the entrypoint logic. It is the backbone of the "write-access" feature.

### Source Code Patching
*   **Purpose:** To overcome hardcoded limitations in the official CLI (IDE host detection and infinite retry).
*   **Mechanism:** A robust shell script (`patch-cli.sh`) invoked during the Docker build.
*   **Target Files:** The script uses `find` to discover target files in both traditional (`dist/src/`) and bundled (`bundle/gemini.js`) structures.
*   **Rule:** If building fails at the patching stage, it means the upstream structure or code patterns have changed. Re-investigate the CLI's source in a temporary container before updating `patch-cli.sh`.
*   **References:** See ADR-0008 (IDE) and ADR-0054 (Infinite Retry).

### Docker-out-of-Docker (DooD)
*   **Concept:** The container mounts `/var/run/docker.sock` from the host and installs the Docker CLI.
*   **Benefit:** You can run `docker build`, `docker run`, or `docker-compose up` from within the agent.
*   **Gotcha:** You are talking to the **Host's Daemon**.
    *   `docker ps` shows host containers.
    *   `docker system prune` cleans the **Host**.
    *   Ports published (`-p 8080:80`) bind to the **Host's** localhost.
