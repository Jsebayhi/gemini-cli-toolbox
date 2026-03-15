# ADR-0061: VPN Sidecar Pattern

## Status
Accepted (Step 3 of Pure Localhost Evolution)

## Context
Currently, the Tailscale VPN daemon (`tailscaled`) is embedded directly within the primary `gemini-cli` and `gemini-hub` Docker images. 

This monolithic approach has several significant drawbacks:
1.  **Image Bloat:** The CLI image must carry the Tailscale binaries and associated networking utilities (`iptables`, `iproute2`), increasing its size and attack surface.
2.  **Privilege Escalation:** The primary container (which runs user code) must be granted `NET_ADMIN` capabilities and access to `/dev/net/tun` to support the embedded VPN.
3.  **Lifecycle Coupling:** If the Tailscale daemon crashes, hangs, or requires re-authentication, the entire Gemini session (and any running tasks) must be restarted to reset the network state.

As we move toward a "User-Choice" architecture where the VPN is optional, the embedded model makes it difficult to cleanly separate the application from the network.

## Decision
We will decouple Tailscale from the primary images by adopting the **VPN Sidecar Pattern**.

### 1. The Container Attachment Strategy
Instead of the traditional Kubernetes sidecar model (where both containers share a Pod network), we will utilize Docker's `container:` network mode:
*   **The Secure Anchor (Parent):** The main `gemini-cli` or `gemini-hub` container will start first, using standard isolated networking (e.g., `--network=bridge`). It will map its ports to `127.0.0.1` as per the "Protected by Default" policy.
*   **The VPN Sidecar:** If `--remote` is requested, the launcher will immediately start a second, lightweight container (the sidecar) running the `tailscale/tailscale` image.
*   **Network Sharing:** The sidecar will be launched with `--network=container:<parent_name>`. This attaches the Tailscale daemon directly to the parent container's network namespace.

### 2. Why Attach to the Parent? (Reverse Sidecar)
Typically, sidecars provide the network namespace, and app containers attach to them. We reverse this to maintain the "Secure Anchor":
*   If the parent container dies, the sidecar loses its network namespace and gracefully exits.
*   If the sidecar dies (or the user manually kills it to disable the VPN), the parent container continues running normally, maintaining its local `127.0.0.1` connectivity. The autonomous agent is not interrupted.

### 3. Naming and Discovery
*   **Naming Convention:** Sidecars will append a `-vpn` suffix to the parent's generated ID (e.g., Parent: `gem-app-cli-1234`, Sidecar: `gem-app-cli-1234-vpn`).
*   **Discovery Filtering:** The Hub's `DockerService` discovery backend must be updated to explicitly ignore containers ending in `-vpn` to prevent them from showing up as duplicate standalone sessions in the UI.

### 4. Image Specialization
*   We will eventually remove Tailscale, `iptables`, and `gosu` (if no longer needed for net setup) from the core images.
*   The Sidecar will use the official, heavily optimized `tailscale/tailscale` image, ensuring we get upstream security patches instantly without rebuilding our CLI tool.

## Consequences
*   **Security:** The main CLI container no longer requires `NET_ADMIN` or `/dev/net/tun`. The attack surface is drastically reduced.
*   **Resilience:** The VPN can be restarted or removed without killing the underlying AI session.
*   **Modularity:** This sets the stage for Step 4 (UI Toggles), as we can now programmatically start or stop the sidecar independently of the main container.
*   **Complexity:** The bash wrapper (`gemini-toolbox`) must now orchestrate the lifecycle of two containers instead of one, requiring careful error handling and cleanup logic.
