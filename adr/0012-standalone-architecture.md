# 2. Hub Standalone Architecture

Date: 2026-01-23

## Status

Supersedes [ADR-0001](./0001-mobile-discovery.md)
Superseded by [ADR-0038](./0038-tailscale-kernel-tun-for-robust-recovery.md)

## Context

In [ADR-0001](./0001-mobile-discovery.md), we decided to mount the host's Tailscale socket (`/var/run/tailscale/tailscaled.sock`) into the Hub container. This allowed "Zero Config" discovery by piggybacking on the host's VPN connection.

However, during implementation and testing, we discovered a critical flaw: **Hosts are not guaranteed to have Tailscale installed.**
*   If the host machine is not joined to the Tailscale network, the Hub (running on the host's LAN IP) cannot reach the Gemini containers (running on VPN IPs).
*   Even if the host *is* on the VPN, mounting the socket is brittle and OS-dependent.

We need an architecture where the Hub works reliably regardless of the host's network configuration.

## Decision

We decided to refactor the Gemini Hub to run as a **Standalone Tailscale Node**.

### 1. Isolated VPN Node
The Hub container now installs the full `tailscale` package (Daemon + CLI).
*   **Action:** When the Hub starts, it spins up its own `tailscaled` process in userspace mode.
*   **Authentication:** It requires a `TAILSCALE_AUTH_KEY` (passed via argument or env var).
*   **Result:** The Hub joins the mesh as a distinct device (e.g., `gemini-hub-a1b2`).

### 2. Host Networking
We switched the container networking mode from `bridge` to `host`.
*   **Why:** Tailscale's userspace networking needs direct access to the host's network interfaces to establish peer-to-peer connections reliably and resolve MagicDNS names.
*   **Trade-off:** We lose port isolation (port 8888 is bound directly to the host), but this is acceptable for a local utility tool.

### 3. Auto-Shutdown
To prevent the Hub from running indefinitely and consuming a VPN license seat/resources, we implemented an **Auto-Shutdown Monitor**.
*   **Logic:** A background thread polls for active Gemini sessions (hostnames starting with `gem-`).
*   **Timeout:** If no sessions are found for **60 seconds**, the Hub terminates itself.
*   **Benefit:** The user doesn't need to manually stop the service. It cleans up after the work session ends.

## Consequences

### Positive
*   **Universal Compatibility:** Works on any Linux host with Docker, regardless of whether Tailscale is installed on the host OS.
*   **Direct Connectivity:** The Hub is on the same virtual network as the Gemini containers, ensuring low-latency visibility.
*   **Resource Efficiency:** The auto-shutdown mechanism ensures the service is ephemeral.

### Negative
*   **Auth Key Requirement:** The user must provide a Tailscale Auth Key to start the Hub. (Mitigated by passing the key from the `gemini-toolbox --remote` command automatically).
