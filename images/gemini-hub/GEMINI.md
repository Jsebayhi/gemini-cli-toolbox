# Component Context: Gemini Hub

This document provides operational context for the `gemini-hub` container.

## 1. Component Overview
A standalone Tailscale node running a Flask-based dashboard for discovering and connecting to active Gemini sessions.

## 2. File Map (Component Level)

| File | Purpose |
| :--- | :--- |
| `Dockerfile` | **The Environment.** Python 3.11-slim, Tailscale daemon + CLI. |
| `docker-entrypoint.sh` | **The Logic.** Starts `tailscaled`, authenticates with `TAILSCALE_AUTH_KEY`, and launches the Flask app. |
| `app.py` | **The Application.** Queries Tailscale status, parses hostnames, and serves the UI with search/filters. Includes the auto-shutdown monitor. |
| `docs/ENGINEERING_STANDARDS.md` | **The Law.** Mandatory coding standards and architectural patterns for this component. |
| `Makefile` | **The Builder.** Local build commands (`build`, `rebuild`) for this image. |
| `adr/` | **The Decisions.** Records explaining the shift to standalone architecture and mobile discovery goals. |

## 3. Core Mandates

### Engineering Standards
*   **Mandate:** All changes to the Python code must adhere to [ENGINEERING_STANDARDS.md](docs/ENGINEERING_STANDARDS.md).
*   **Key Rules:** Use `requirements.txt`, separate logic from Flask routes, and strictly type-hint all functions.

## 4. Operational Workflows

### Building (Local)
Run from `images/gemini-hub/`:
```bash
make build
# or
make rebuild
```

### Testing
We use `pytest` for unit and integration tests, and **Playwright** for UI tests.
```bash
# Run unit and integration tests
make test

# Run UI tests (requires building the test image with browsers)
make test-ui
```

### Manual Run
```bash
# Requires an auth key
docker run --rm -it \
    --net=host \
    --cap-add=NET_ADMIN \
    --device /dev/net/tun \
    -e TAILSCALE_AUTH_KEY=tskey-auth-... \
    gemini-cli-toolbox/hub:latest
```

## 5. Known Peculiarities & Gotchas

### Host Networking
The Hub uses `--net=host` to ensure reliable peer discovery and MagicDNS resolution within the Tailscale mesh. This binds port 8888 directly to the host's network interfaces.

### Hybrid Mode (Local Discovery)
*   **Concept:** To reduce latency when the user is on the same physical machine as the container, the Hub attempts to offer a `localhost` link.
*   **Mechanism:** It runs `docker ps` to inspect active containers. If it finds a container name matching a Tailscale peer that exposes port 3000 to the host (e.g., `0.0.0.0:32768->3000/tcp`), it enriches the UI with a "LOCAL" badge linking to `http://localhost:32768`.

### Launch Parity & Constraints
*   **Advanced Options:** The Hub supports most `gemini-toolbox` flags (Preview, No-IDE, No-Docker, Worktrees, Custom Image, and Extra Docker Args).
*   **TMUX Mandate:** The `--no-tmux` flag is **explicitly forbidden** in the Hub UI. 
    *   **Reason:** The Hub always launches sessions with `--remote` to enable web-based access via `ttyd`. `ttyd` relies on `tmux` to serve the terminal. Disabling TMUX would cause the session to be unreachable remotely and the container to exit immediately.

### Auto-Shutdown
The Hub will automatically terminate after **60 seconds** of inactivity (when no hostnames starting with `gem-` are detected in the Tailnet). This is intentional to save resources and VPN license seats.

### Automatic Worktree Discovery
*   **Concept:** To ensure ephemeral worktrees are scannable without manual configuration, the Hub automatically includes `GEMINI_WORKTREE_ROOT` in its `HUB_ROOTS` list.
*   **Benefit:** Users can browse and launch sessions from the Hub's exploration cache by default.

### Worktree Pruning
The Hub runs a background `PruneService` to manage the ephemeral worktree cache.
*   **Toggle:** `HUB_WORKTREE_PRUNE_ENABLED` (Default: `true`).
*   **Retention Periods:**
    *   `GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS`: Retention for anonymous/headless worktrees (Default: `30`).
    *   `GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS`: Retention for named branch worktrees (Default: `90`).
    *   `GEMINI_WORKTREE_ORPHAN_EXPIRY_DAYS`: Retention for ambiguous or unreadable worktrees (Default: `90`).
*   **Mechanism:** Uses `git symbolic-ref` for classification and directory `mtime` for aging.

### Naming Constraint
The Hub relies on the naming convention documented in the root `GEMINI.md`. It extracts project names and types by parsing hostnames from the right side, assuming the type segment (e.g., `geminicli`) contains no hyphens.

### Profile-Specific Arguments (extra-args)
Each configuration profile (subdirectory in `HOST_CONFIG_ROOT`) can contain a file named `extra-args`. If present, the Hub (via `gemini-toolbox`) will load these arguments as if they were passed to the CLI.

*   **Semantics:** **Toolbox Arguments**. You can use any flag accepted by `gemini-toolbox` (e.g., `--preview`, `--no-ide`, `--volume`, `--env`).
*   **Format:** One argument per line is recommended.
*   **Precedence:** Arguments in the file are applied *before* the CLI arguments (meaning CLI arguments can override profile defaults).
*   **Location:** `${HOST_CONFIG_ROOT}/{profile_name}/extra-args`
