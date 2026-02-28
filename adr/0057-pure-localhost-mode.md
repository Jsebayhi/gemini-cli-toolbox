# ADR-0057: Pure Localhost and Hybrid Mode

## Status
Proposed

## Context
The Gemini CLI Toolbox currently relies heavily on Tailscale for networking and discovery. While effective for remote access, users often want to use the Hub and sessions locally without a VPN, either due to connectivity issues, corporate policies, or simple preference.

The existing "Standard Mode" (`--net=host`) is easy to use but lacks isolation and can be reachable on the local network (LAN) if the host firewall is permissive.

## Decision
We will introduce a "Pure Localhost" mode across the entire toolbox and enforce a "Protected by Default" networking policy.

### 1. Networking Possibility Matrix

| Hub Mode | Session Requested | VPN (Tailscale) | Localhost (127.0.0.1) | LAN Reachable | Resulting Flags |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Localhost** | Local (Protected) | Off | **On** | No | `--no-vpn` |
| **Localhost** | VPN + Local | **On** | **On** | No | `--remote` (provided key exists) |
| **Localhost** | VPN Only | **On** | Off | No | `--remote --no-localhost` |
| **VPN** | Local (Protected) | Off | **On** | No | `--no-vpn` |
| **VPN** | VPN + Local | **On** | **On** | No | `--remote` |
| **VPN** | VPN Only | **On** | Off | No | `--remote --no-localhost` |
| **Any** | Legacy Raw Host | Off | **On** (All IPs) | **Yes** | `--net=host` |

### 2. "Protected by Default" Policy
For maximum security, the toolbox will default to "Protected Localhost" mode:
*   **Sessions:** Use `--network=bridge` and bind port 3000 strictly to `127.0.0.1` (e.g., `-p 127.0.0.1:0:3000`). This ensures sessions are NEVER reachable via the LAN.
*   **VPN Sessions:** When `--remote` is used, the container will *also* expose its port to `127.0.0.1` by default, allowing simultaneous local and remote access.
*   **Opt-out:** A new flag `--no-localhost` will be added to disable the host port mapping (useful for VPN-only sessions).

### 3. The `--no-vpn` Flag
A new flag `--no-vpn` will be added to `gemini-toolbox` and `gemini-hub`.

*   **For Sessions (`gemini-toolbox`):**
    *   Disables Tailscale initialization.
    *   Enforces "Protected by Default" policy (Bridge + 127.0.0.1 mapping).
*   **For the Hub (`gemini-hub`):**
    *   Makes `TAILSCALE_AUTH_KEY` optional.
    *   Disables Tailscale daemon startup if no key is provided and `--no-vpn` is set.
    *   Continues to bind to `127.0.0.1:8888`.

### 4. Unified Discovery
The Hub's discovery service (`TailscaleService`) will be refactored to perform "Unified Discovery":
*   It will query both `tailscale status` (if available) and `docker ps`.
*   Any container starting with `gem-` found via `docker ps` will be included in the list, even if it is not a Tailscale peer.
*   Containers found in both will be marked as "Hybrid" (VPN + Local).
*   Containers found only in `docker ps` will be marked as "Local Only".

### 5. Hub Launch Wizard
The Hub Launch Wizard will offer "VPN Mode" if a key is available (regardless of whether the Hub itself is using VPN). It will also offer a toggle to disable Localhost access for VPN-enabled sessions.

## Consequences
*   **Security:** Improved security for local usage by strictly binding to `127.0.0.1` by default.
*   **Flexibility:** Users can use the Hub and sessions completely offline or without a Tailscale account.
*   **Complexity:** The discovery logic becomes slightly more complex as it must merge two different sources of truth.
*   **Consistency:** Maintains the 1:1 naming scheme but allows it to function without MagicDNS.
