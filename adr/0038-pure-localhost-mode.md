# ADR 0038: Pure Localhost Mode (No VPN)

## Status
Proposed

## Context
Currently, the Gemini Hub is designed as a standalone Tailscale node. It requires a `TAILSCALE_AUTH_KEY` to start and relies primarily on `tailscale status` for peer discovery.
While it has a "Hybrid Mode" that discovers local containers via `docker ps`, this is currently an enrichment step for peers already found in the Tailnet.
Users want to be able to use the Gemini CLI and the Hub in a "pure localhost mode", where no VPN is required, and all interactions happen on the local machine.

## Decision
We will decouple the Hub's core functionality from the Tailscale requirement and introduce an explicit toggle.

### 1. Explicit Local Mode (`--local` flag)
`bin/gemini-hub` and `bin/gemini-toolbox` will gain a `--local` flag.
- When `--local` is present, the Hub will skip Tailscale authentication entirely, even if a key is available in the environment (`GEMINI_REMOTE_KEY`).
- If no key is provided and `--local` is *not* present, the Hub will fallback to localhost mode with a warning.
- The `docker-entrypoint.sh` in the Hub image will be updated to handle the absence of `TAILSCALE_AUTH_KEY` gracefully (skip `tailscale up` but continue to `python run.py`).

### 2. Unified Discovery Logic
`TailscaleService` will be updated to:
- **Primary:** Query `docker ps` for all `gem-*` containers. This ensures all local sessions are visible regardless of VPN status.
- **Secondary:** Query `tailscale status` (if the daemon is running).
- **Merge:** Match local containers with Tailscale nodes by hostname. Containers found only via Docker are labeled "LOCAL".

### 3. Hybrid Connectivity & Isolation
A Hub running in `--local` mode **can still launch remote sessions** if a key is provided (via `--key` or environment).
- **Downstream Provisioning:** The Hub passes its `TAILSCALE_AUTH_KEY` to any session launched with the remote flag.
- **Isolation:** Because the Hub itself is not authenticated to Tailscale, it **cannot** discover or connect to sessions running on *other* hosts via the VPN. It only manages and displays sessions running on the **same host** (discovered via `docker ps`).
- **Access:** The Hub is accessible only via `localhost:8888`. Sessions it launches are accessible via `localhost:<random_port>` (Hybrid Mode) and optionally via VPN IP.

### 4. Context-Aware Defaults & UI
The Hub will track its own startup mode via a `HUB_MODE` environment variable.

- **Visual Indicator:** The Hub UI will display a prominent "MODE: VPN" or "MODE: LOCAL" badge in the header to inform the user of its connectivity state.
- **Session Defaults:**
    - **Local Hub:** The "Remote Access (VPN)" toggle in the launch wizard will be **unchecked** by default. Helper text will indicate: "◈ Pre-selected (Local Hub)".
    - **VPN Hub:** The "Remote Access (VPN)" toggle will be **checked** by default. Helper text will indicate: "◈ Pre-selected (VPN Hub)".
- **Transparency:** The launch wizard will explicitly show the "Remote Access (VPN)" toggle, allowing the user to override the default before launching.

### 5. Auto-shutdown Monitor
The `MonitorService` will count both local Docker containers and Tailscale peers to determine inactivity.

## Alternatives Considered

### Alternative 1: Strict Mode Toggle (`--local` flag)
Introduce a `--local` flag that explicitly disables Tailscale.
- *Rejection Reason:* Adds complexity to the CLI interface and requires the user to know which mode they want. Automatic discovery is more user-friendly.

### Alternative 2: Separate "Local Hub" Image
Create a different Docker image for local-only use.
- *Rejection Reason:* Increases maintenance burden and goes against the "standalone architecture" goal where one image should handle both local and remote scenarios.

## Consequences
- The Hub becomes more robust and usable in offline or restricted network environments.
- The term "TailscaleIP" in the UI might need to be generalized to "Address" or handled conditionally.
- Users can now start the Hub simply with `gemini-hub` (assuming no key is needed/provided).
