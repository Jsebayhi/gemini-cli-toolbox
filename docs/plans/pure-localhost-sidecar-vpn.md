# Implementation Plan: Pure-localhost & Sidecar VPN

This document outlines the 11-step incremental implementation plan for moving the Gemini CLI Toolbox to a "Protected by Default" networking architecture using modular Sidecars.

## End Goal
A secure, modular, and highly available networking architecture where:
1.  **Sessions are private by default:** All sessions run in bridge mode, bound strictly to `127.0.0.1` on the host, making them invisible to the local network (LAN).
2.  **Connectivity is a Plug-in:** Remote access (VPN) is handled by ephemeral sidecar containers that share the network and PID namespaces of the parent session.
3.  **Unified Management:** The Gemini Hub manages both local and remote connectivity tiers through a single dashboard, with zero-downtime tier switching.
4.  **Bulletproof Cleanup:** Sidecars automatically self-terminate when their parent session exits, preventing resource leaks.

---

## Phase 1: The Localhost Foundation (Pure Localhost)

### Step 1: Secure Anchor (Networking Refactor)
*   **Goal:** Move away from insecure host networking to bridge isolation.
*   **Plan:** 
    *   Modify `bin/gemini-toolbox` and `bin/gemini-hub` to use `--network=bridge`.
    *   Implement default port mapping `-p 127.0.0.1:0:3000` for sessions and `-p 127.0.0.1:8888:8888` for the Hub.
    *   Add `--no-vpn`, `--no-localhost`, and `--network-host` (legacy) flags.
*   **Done when:** `gemini-toolbox` starts a container in bridge mode bound only to loopback.

### Step 2: Hub Docker Discovery (Backend)
*   **Goal:** Enable the Hub to "see" sessions without Tailscale IPs.
*   **Plan:** 
    *   In `images/gemini-hub/app/services/tailscale.py`, implement `get_local_ports()`.
    *   Use `docker ps --format '{{.Names}}|{{.Ports}}'` to identify `gem-` containers mapping port 3000.
    *   Refactor `parse_peers()` to merge results from `docker ps` and `tailscale status`.
*   **Done when:** The `TailscaleService` returns local containers in its session list.

### Step 3: Hub Local UI (Frontend)
*   **Goal:** Provide a way to connect to local sessions via the dashboard.
*   **Plan:** 
    *   Add a `[LOCAL]` badge to session cards in `index.html`.
    *   In `main.js`, update the "Open" link to prioritize the `localhost` URL if available.
*   **Done when:** The Hub dashboard displays local sessions with a clickable `[LOCAL]` link.

---

## Phase 2: Sidecar Infrastructure

### Step 4: VPN Sidecar Image
*   **Goal:** Create a lightweight, reusable VPN connectivity provider.
*   **Plan:** 
    *   Create `images/gemini-vpn/Dockerfile` (based on `tailscale/tailscale`).
    *   Implement `images/gemini-vpn/docker-entrypoint.sh` with a PID-1 watchdog (`while [ -d /proc/1 ]; do sleep 5; done`).
*   **Done when:** The `gemini-vpn` image can be built and self-terminates when its PID-1 parent exits.

### Step 5: Toolbox Sidecar Orchestration
*   **Goal:** Add manual sidecar management to the CLI.
*   **Plan:** 
    *   Implement `vpn-add`, `vpn-stop`, and `vpn-prune` commands in `bin/gemini-toolbox`.
    *   Use `--network container:{ID}` and `--pid container:{ID}` to attach sidecars.
*   **Done when:** `gemini-toolbox vpn-add <id>` successfully attaches a functional VPN node to a running session.

### Step 6: Refactor `--remote`
*   **Goal:** Standardize session startup to use the sidecar model.
*   **Plan:** 
    *   Modify the `--remote` flag in `bin/gemini-toolbox` to launch the main container FIRST, then immediately spawn the VPN sidecar.
    *   Remove legacy Tailscale initialization logic from `docker-entrypoint.sh`.
*   **Done when:** `gemini-toolbox --remote <key>` starts two containers (Session + VPN) instead of one.

---

## Phase 3: Hub Connectivity Management

### Step 7: Hub VPN Toggles (API & UI)
*   **Goal:** Single-click tier switching from the dashboard.
*   **Plan:** 
    *   Add `/api/vpn/[add|stop]` routes to `images/gemini-hub/app/api/routes.py`.
    *   Add `🌐 +VPN` and `🌐 VPN` toggle buttons to session cards in the UI.
*   **Done when:** Clicking `+VPN` on a local-only session card spawns a VPN sidecar.

### Step 8: Bulk VPN Management
*   **Goal:** synchronize connectivity for all active sessions.
*   **Plan:** 
    *   Add `vpn-add --all` and `vpn-stop --all` to `bin/gemini-toolbox`.
    *   Add "START ALL VPN" and "STOP ALL VPN" global buttons to the Hub dashboard.
*   **Done when:** One click can enable VPN for multiple running sessions simultaneously.

### Step 9: Hub Self-Upgrade
*   **Goal:** Remote access to the Hub itself.
*   **Plan:** 
    *   Update `bin/gemini-hub` with `vpn-add` / `vpn-stop` commands targeting its own container.
    *   Allow the Hub to attach a VPN sidecar to itself on-demand.
*   **Done when:** `gemini-hub vpn-add` makes the Hub dashboard reachable via Tailscale.

---

## Phase 4: Final Hardening & Cleanup

### Step 10: Sealed Mode Sandbox
*   **Goal:** Provide a maximum-isolation "one-click" sandbox.
*   **Plan:** 
    *   Add `--sealed` flag to `bin/gemini-toolbox`.
    *   Sealed mode automatically sets: `--no-docker`, `--no-ide`, and `--no-localhost`.
*   **Done when:** `--sealed` containers run with no host integrations or network exposure.

### Step 11: Decoupling Cleanup
*   **Goal:** Minimize image footprint and finalize documentation.
*   **Plan:** 
    *   Surgically remove `tailscale` and `iptables` from `images/gemini-base` (and child images).
    *   Finalize ADR-0057, ADR-0058, and ADR-0059.
    *   Update root `README.md` to document the 2-tier architecture.
*   **Done when:** `make local-ci` passes and images no longer contain redundant networking tools.
