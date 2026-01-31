# 1. Gemini Hub for Mobile Discovery

Date: 2026-01-23

## Status

Superseded by [ADR-0002](./0002-standalone-architecture.md)

## Context

The "Remote Access" feature (via Tailscale) allows users to access their Gemini CLI session from a mobile device. However, the connection process was high-friction:
1.  **Dynamic IPs:** Tailscale assigns IPs/MagicDNS names.
2.  **Manual Discovery:** The user had to run `tailscale status`, find the IP, and manually type `http://100.x.y.z:3000` into their phone's browser.
3.  **Typing Pain:** Typing IP addresses or long DNS names on mobile keyboards is error-prone and tedious.

We needed a "Zero Config" way for a user to just open their phone and see their active sessions.

## Decision

We decided to implement **Gemini Hub**, a lightweight web dashboard that runs on the user's host machine.

### 1. Architecture: Dockerized Service
We chose to package the Hub as a Docker container (`images/gemini-hub`) rather than a host-level Python script.
*   **Reasoning:** We strictly adhere to the "No Host Dependencies" rule. We cannot assume the user has Python 3, Flask, or the correct libraries installed.
*   **Trade-off:** Requires building/downloading another (small) image.

### 2. Network Integration: Host Socket Mounting
The Hub needs to know the status of the Tailscale network.
*   **Option A (Rejected): Standalone Tailscale Node.** Run `tailscaled` inside the Hub container with its own Auth Key.
    *   *Pros:* Complete isolation.
    *   *Cons:* Requires the user to generate *another* auth key just for the Hub. High friction.
*   **Option B (Accepted): Host Socket Mount.** Mount `/var/run/tailscale/tailscaled.sock` from the host into the container.
    *   *Pros:* **Zero Config.** The Hub sees exactly what the Host sees. No auth keys required.
    *   *Cons:* Requires the host to be a Linux machine with Tailscale installed (which is already a prerequisite for the Toolbox on Linux).

### 3. Distribution Strategy: Single Repository, Distinct Tag
We publish the Hub image to the existing Docker Hub repository `jsebayhi/gemini-cli-toolbox` using the tag `:latest-hub`.
*   **Reasoning:** The Hub is an auxiliary utility tightly coupled to the Toolbox. It is not a standalone product.
*   **Benefit:** Simplifies access management and documentation. Users pull from one place.

### 4. Launcher Integration: Auto-Start
We updated `bin/gemini-toolbox` to automatically check for and start the Hub when the `--remote` flag is used.
*   **Reasoning:** The Hub is an implementation detail of the "Remote Experience". The user shouldn't have to remember to start a separate service. "It just works."

## Consequences

### Positive
*   **UX Upgrade:** Users bookmark **one** URL (`http://gemini-hub:8888`) on their phone and never type an IP again.
*   **Stateless:** The Hub has no database. It queries the network state in real-time.
*   **Secure:** The dashboard is only exposed to the local network (and the Tailscale mesh), not the public internet.

### Negative
*   **Linux Specific:** The socket mount strategy relies on the standard Linux path `/var/run/tailscale/tailscaled.sock`. This may require adaptation for macOS/Windows in the future.
