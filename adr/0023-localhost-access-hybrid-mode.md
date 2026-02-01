# ADR 0023: Localhost Access (Hybrid Mode)

## Status
Accepted

## Context
Remote sessions (via Tailscale VPN) provide excellent mobility but introduce a critical dependency: **The user must be connected to the VPN to access a container running on their own machine.**

This creates significant friction:
1.  **Dependency:** If the host's Tailscale daemon is stopped, paused, or misconfigured, the user is locked out of their local session.
2.  **Overhead:** Routing local traffic through a VPN tunnel (tun device) introduces unnecessary overhead and complexity for a "localhost" scenario.

The goal is to allow **Hybrid Access**:
*   **Localhost:** Direct, zero-dependency access when on the host machine.
*   **VPN:** Secure remote access when on mobile/remote devices.

## Decision
We will implement an automated port-mapping and discovery mechanism called **Hybrid Mode**.

### 1. Ephemeral Port Binding
The `gemini-toolbox` wrapper is updated to bind the container's standard web port (3000) to a random ephemeral port on the host's loopback interface (`127.0.0.1`).
*   **Command:** `-p 127.0.0.1:0:3000`
*   **Rationale:** Using `:0` avoids port conflicts when running multiple sessions. Binding to `127.0.0.1` ensures the port is NOT exposed to the local network (preserving the security of the sandbox).

### 2. Hub-Side Discovery
The Gemini Hub backend is enhanced to perform "Cross-Daemon Discovery":
*   It executes `docker ps` to find containers matching the `gem-*` pattern.
*   It parses the port mapping (e.g., `127.0.0.1:32768->3000/tcp`).
*   It enriches the session metadata with a `local_url` (`http://localhost:32768`).

### 3. Smart UI (Client-Side Logic)
To prevent confusing users on remote devices or disconnected hosts, the Hub frontend employs **Active Connectivity Probing**:

1.  **Dual Probe:** On load, the client attempts to `fetch()` both the `local_url` (if on localhost) and the `vpn_url` (Tailscale IP).
2.  **Smart Prioritization:**
    *   **If Localhost is reachable:** The Primary Card Link becomes the **Local URL**.
    *   **If VPN is reachable:** The Badge becomes visible and links to the **VPN URL**.
    *   **Fallback:** If Localhost is unreachable (e.g., remote phone), the Primary Link remains the VPN URL.
3.  **Launch Wizard:** The "Connect" button dynamically upgrades to "Connect (Local) ⚡" if the Local URL is resolved, minimizing UI clutter.

## Consequences
*   **Positive:** Near-zero latency for local development.
*   **Positive:** Reliable access even when Tailscale is disconnected on the host.
*   **Positive:** Simplified UI; the user doesn't have to manually track random ports.
*   **Negative:** The Hub container now requires access to the host's Docker socket (DooD) to perform discovery.
*   **Negative:** Added complexity in the Hub frontend to handle conditional link swapping.
