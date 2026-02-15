# 0038. Tailscale Kernel TUN Mode for Robust Connectivity Recovery

## Status
Proposed

## Context
Remote sessions (Gemini CLI and Hub) become inaccessible via Tailscale after the host machine wakes up from sleep. 

This decision supersedes the "Host Networking" decision in [ADR-0012](./0012-standalone-architecture.md).

Currently, both components start `tailscaled` using `--tun=userspace-networking`. This mode was chosen for maximum compatibility (working without `/dev/net/tun`), but it is less robust to network environment changes because it relies on a userspace TCP/IP stack (netstack) that might not correctly detect or recover from the host's physical network interface going down and up.

Since the `gemini-toolbox` and `gemini-hub` scripts already pass `--cap-add=NET_ADMIN` and `--device /dev/net/tun` to the containers, we have the necessary privileges to use the standard Linux Kernel TUN device.

## Alternatives Considered

### 1. Connectivity Watchdog
*   **Description:** Add a background process (e.g., a shell loop or a Python thread) that periodically pings the tailnet or checks `tailscale status`. If connectivity is lost, it restarts the `tailscaled` process or runs `tailscale up`.
*   **Pros:** Works with the existing `userspace-networking` mode.
*   **Cons:** Reactive rather than proactive. Adds complexity to the entrypoint scripts and Hub services. Might cause unnecessary service disruptions during brief flaps.
*   **Status:** Rejected
*   **Reason for Rejection:** It addresses the symptom rather than the root cause. Kernel-level networking is inherently more robust for this use case.

### 2. Aggressive `tailscale up` Polling
*   **Description:** Periodically execute `tailscale up --authkey...` inside the container to "refresh" the registration and trigger a reconnect.
*   **Pros:** Very simple to implement.
*   **Cons:** Potentially creates a lot of noise in Tailscale logs and control plane. Does not fix the underlying userspace stack getting stuck.
*   **Status:** Rejected
*   **Reason for Rejection:** Inefficient and doesn't guarantee recovery if the daemon itself is in a bad state.

### 3. Tailscale Kernel TUN Mode (Selected)
*   **Description:** Remove the `--tun=userspace-networking` flag from the `tailscaled` startup command. This forces Tailscale to use the `/dev/net/tun` device to create a `tailscale0` network interface.
*   **Pros:**
    *   **Robustness:** The Linux kernel handles the network interface state and routing, which is much more resilient to host sleep/wake cycles.
    *   **Performance:** Native kernel-space networking is faster than userspace netstack.
    *   **Standardization:** This is the recommended way to run Tailscale on Linux when privileges are available.
*   **Cons:** Requires `NET_ADMIN` and `/dev/net/tun` (but these are already requirements for the current Toolbox remote mode).
*   **Status:** Selected
*   **Reason for Selection:** Leverages existing privileges to provide a more stable and "native" networking experience that is known to handle network changes better.

## Decision
We will switch both `gemini-cli` and `gemini-hub` to use Kernel TUN mode by default.

1.  Modify `images/gemini-cli/docker-entrypoint.sh` to remove `--tun=userspace-networking`.
2.  Modify `images/gemini-hub/docker-entrypoint.sh` to remove `--tun=userspace-networking`.
3.  Ensure `tailscaled` is started with a persistent state directory (already implemented for Hub, needs verification for CLI).

## Consequences

### Positive
*   **Improved Recovery:** Remote sessions should automatically reconnect once the host network is restored after sleep.
*   **Better Performance:** Reduced CPU overhead compared to userspace networking.
*   **Simplified Troubleshooting:** Standard network tools (`ip addr`, `ip route`) can be used inside the container to inspect the Tailscale interface.

### Negative
*   **Hard Dependency on TUN:** Containers will fail to start in remote mode if `/dev/net/tun` is missing or `NET_ADMIN` is not granted. This is acceptable as the CLI already enforces these for remote mode.

## Security & Privilege Analysis

The transition to Kernel TUN mode requires the following host-level privileges:
1.  **`--cap-add=NET_ADMIN`**: Allows the container to manage its own network interfaces and routing tables.
2.  **`--device /dev/net/tun`**: Provides access to the host's virtual tunnel driver.

### Risk Assessment
*   **Host Escape:** These privileges do **not** grant the ability to escape the container or access the host filesystem. While `NET_ADMIN` is an elevated capability, it is restricted to the container's network namespace.
*   **Network Interference:** A compromised container could theoretically attempt to spoof traffic or scan the local network, but it cannot modify the host's primary physical network interfaces (e.g., eth0, wlan0) unless `--net=host` is also used.
*   **Comparison to DooD:** The risk posed by these networking privileges is significantly lower than the existing (and documented) risk of **Docker-out-of-Docker (`/var/run/docker.sock`)**, which provides a direct path to host root access.

### Recommendation
Users concerned about maximum isolation should avoid using the `--remote` flag and run the container in "Sandbox Mode" by passing `--no-docker` and ensuring no VPN keys are provided. For standard development usage, the convenience of robust remote access outweighs the incremental risk of these networking capabilities.
