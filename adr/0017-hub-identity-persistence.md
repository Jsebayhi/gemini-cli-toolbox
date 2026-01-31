# ADR 0005: Hub Identity Persistence

## Status
Accepted

## Context
The Gemini Hub relies on Tailscale MagicDNS to be accessible via `http://gemini-hub:8888`.
However, Tailscale assigns a unique "Device ID" and "Node Key" to every machine. By default, running a container generates a new identity every time.

**The Problem:**
1.  User runs Hub -> Assigned `gemini-hub` (IP: 100.1.2.3).
2.  User stops Hub.
3.  User runs Hub again -> New Identity. Tailscale sees a conflict and renames it `gemini-hub-1`.
4.  User tries to access `http://gemini-hub`.
    *   **Result:** DNS resolution fails or points to the old (dead) IP.

## Decision
We implement a **Hybrid Persistence Strategy** to maximize the stability of the `gemini-hub` DNS name.

### 1. Named Docker Volume
We use a Docker Named Volume `gemini-hub-state` mounted to `/var/lib/tailscale` inside the container.
*   **Why:** This persists the `tailscaled.state` file (containing the Private Key and Device ID) across container restarts.
*   **Result:** Tailscale recognizes the restarting container as the **same device**. No name change, no IP change.
*   **Why Named Volume?** Unlike a bind mount (e.g., `~/.gemini/state`), a named volume is managed by Docker and doesn't clutter the user's home directory.

### 2. Aggressive Re-Auth
We append `--force-reauth` to the `tailscale up` command.
*   **Why:** If the user manually deletes the `gemini-hub-state` volume (or it's a fresh install), the container will start with a fresh identity.
*   **Result:** `--force-reauth` tells Tailscale to aggressively take over the `gemini-hub` hostname, even if an old device record exists, reducing the chance of getting a `gemini-hub-1` fallback name.

## Consequences
*   **Positive:** Stable DNS name (`gemini-hub`) in 99% of cases.
*   **Positive:** Clean host filesystem (no hidden state files in user dirs).
*   **Negative:** Requires a Docker Volume which persists until manually removed (`docker volume rm gemini-hub-state`).
