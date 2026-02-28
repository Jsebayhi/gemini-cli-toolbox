# ADR-0057: Pure Localhost Mode

## Status
Proposed

## Context
The Gemini CLI Toolbox currently relies heavily on Tailscale for networking and discovery. While effective for remote access, users often want to use the Hub and sessions locally without a VPN, either due to connectivity issues, corporate policies, or simple preference.

The existing "Standard Mode" (`--net=host`) is easy to use but lacks isolation and can be reachable on the local network (LAN) if the host firewall is permissive.

## Decision
We will introduce a "Pure Localhost" mode across the entire toolbox.

### 1. The `--no-vpn` Flag
A new flag `--no-vpn` will be added to `gemini-toolbox` and `gemini-hub`.

*   **For Sessions (`gemini-toolbox`):**
    *   Disables Tailscale initialization.
    *   Uses `--network=bridge` for network isolation.
    *   Automatically maps port 3000 to a random host port on `127.0.0.1` (e.g., `-p 127.0.0.1:0:3000`). This ensures the session is reachable only from the host machine.
*   **For the Hub (`gemini-hub`):**
    *   Makes `TAILSCALE_AUTH_KEY` optional.
    *   Disables Tailscale daemon startup if no key is provided and `--no-vpn` is set.
    *   Continues to bind to `127.0.0.1:8888`.

### 2. Unified Discovery
The Hub's discovery service (`TailscaleService`) will be refactored to perform "Unified Discovery":
*   It will query both `tailscale status` (if available) and `docker ps`.
*   Any container starting with `gem-` found via `docker ps` will be included in the list, even if it is not a Tailscale peer.
*   Containers found in both will be marked as "Hybrid" (VPN + Local).
*   Containers found only in `docker ps` will be marked as "Local Only".

### 3. UI/UX Enhancements
*   The Hub UI will distinguish between VPN and Local-only sessions.
*   The "Launch Wizard" will automatically adapt: if the Hub is running in "No VPN" mode, it will default to launching sessions with `--no-vpn`.

## Consequences
*   **Security:** Improved security for local usage by strictly binding to `127.0.0.1`.
*   **Flexibility:** Users can use the Hub and sessions completely offline or without a Tailscale account.
*   **Complexity:** The discovery logic becomes slightly more complex as it must merge two different sources of truth.
*   **Consistency:** Maintains the 1:1 naming scheme but allows it to function without MagicDNS.
