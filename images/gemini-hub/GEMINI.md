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

### Auto-Shutdown
The Hub will automatically terminate after **60 seconds** of inactivity (when no hostnames starting with `gem-` are detected in the Tailnet). This is intentional to save resources and VPN license seats.

### Naming Constraint
The Hub relies on the naming convention documented in the root `GEMINI.md`. It extracts project names and types by parsing hostnames from the right side, assuming the type segment (e.g., `geminicli`) contains no hyphens.

### Profile-Specific Arguments (extra-args)
Each configuration profile (subdirectory in `HOST_CONFIG_ROOT`) can contain a file named `extra-args`. If present, the Hub (via `gemini-toolbox`) will load these arguments as if they were passed to the CLI.

*   **Semantics:** **Toolbox Arguments**. You can use any flag accepted by `gemini-toolbox` (e.g., `--full`, `--no-ide`, `--volume`, `--env`).
*   **Format:** One argument per line is recommended.
*   **Precedence:** Arguments in the file are applied *before* the CLI arguments (meaning CLI arguments can override profile defaults).
*   **Location:** `${HOST_CONFIG_ROOT}/{profile_name}/extra-args`
```