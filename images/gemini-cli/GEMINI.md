# Component Context: Gemini CLI

This document provides operational context for AI agents working specifically on the `gemini-cli` container.

## 1. Component Overview
A Debian-based Docker image wrapping the `@google/gemini-cli`. It focuses on seamless host integration (permissions, networking, volumes).

## 2. File Map (Component Level)

| File | Purpose |
| :--- | :--- |
| `Dockerfile` | **The Environment.** Node.js 20 (Bookworm), `gosu`, and the CLI tool. |
| `docker-entrypoint.sh` | **The Logic.** Runtime script that fixes permissions and switches user via `gosu`. |
| `index.html` | **The UI.** Custom ttyd template for mobile-friendly remote access (keyboard handling). |
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

### The "Input Lag" Issue
*   **Symptom:** Severe latency when typing in the interactive chat.
*   **Cause:** Large host configuration folder (`~/.gemini`) causing slow synchronous I/O.
*   **Fix:** Clean the host configuration folder.

### Permission Architecture
*   **Concept:** The container starts as `root`, creates a user matching `DEFAULT_UID` (from host), fixes ownership of `/home/gemini`, and drops privileges via `gosu`.
*   **Rule:** Never remove `gosu` or the entrypoint logic. It is the backbone of the "write-access" feature.

### Docker-out-of-Docker (DooD)
*   **Concept:** The container mounts `/var/run/docker.sock` from the host and installs the Docker CLI.
*   **Benefit:** You can run `docker build`, `docker run`, or `docker-compose up` from within the agent.
*   **Gotcha:** You are talking to the **Host's Daemon**.
    *   `docker ps` shows host containers.
    *   `docker system prune` cleans the **Host**.
    *   Ports published (`-p 8080:80`) bind to the **Host's** localhost.
