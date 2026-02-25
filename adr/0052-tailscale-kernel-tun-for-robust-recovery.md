# ADR-0052: Tailscale Kernel TUN Mode for Robust Connectivity Recovery

## Status
Proposed

## Context
Remote sessions (Gemini CLI and Hub) become inaccessible via Tailscale after the host machine wakes up from sleep. 

This decision supersedes the "Host Networking" decision in [ADR-0012](./0012-standalone-architecture.md).

### The Connectivity Problem
Currently, both components start `tailscaled` using `--tun=userspace-networking`.
*   **Userspace Networking (Old):** Tailscale runs its own TCP/IP stack (netstack) entirely within the `tailscaled` process. It doesn't create a real network interface on the OS.
*   **The Issue:** Because this stack is detached from the host kernel's networking events, it often fails to correctly re-detect or recover when physical network interfaces (WiFi/Ethernet) go down and up during a sleep/wake cycle. The userspace stack gets "stuck," rendering the session unreachable until the container is restarted.

### The Isolation Problem
The Gemini Hub was previously using `--net=host` to ensure Tailscale could resolve peer names.
*   **The Issue:** This shared the host's entire network namespace, exposing the Hub's management port (8888) to the entire local network (LAN/WiFi). Any device on the same network could potentially reach the dashboard if they knew the host's local IP.

## Decision

We will transition the Gemini CLI Toolbox to a "Kernel-Native, Zero-Trust Local" networking model.

### 1. Tailscale Kernel TUN Mode
We will remove the `--tun=userspace-networking` flag from the `tailscaled` startup command in all components.
*   **Action:** Tailscale will use the `/dev/net/tun` device to create a virtual `tailscale0` network interface.
*   **Why:** The Linux kernel handles the network interface state and routing natively. Standard kernel networking triggers (routing updates, interface state changes) allow Tailscale to recover the tunnel natively and nearly instantaneously after the host wakes from sleep.

### 2. Hub Bridge Networking & Loopback Binding
We will refactor the Gemini Hub to use standard Docker Bridge Networking instead of Host Networking.
*   **Action:** Switch to `--network=bridge`.
*   **Port Mapping:** Explicitly map the management port to the host loopback interface only: `-p 127.0.0.1:8888:8888`.
*   **Why:** This ensures that the Hub UI is **only** reachable from the host machine itself or through the secure Tailscale VPN. It is completely isolated from the local physical network (WiFi/LAN).

### 3. Privilege Requirements
Since the `gemini-toolbox` and `gemini-hub` scripts already pass the necessary flags, we will officially mandate them for remote mode:
*   `--cap-add=NET_ADMIN`: Required to create and manage the `tailscale0` interface.
*   `--device /dev/net/tun`: Required to access the host's tunnel driver.

## Alternatives Considered

### 1. Connectivity Watchdog
*   **Description:** Add a background process that periodically pings the tailnet and restarts `tailscaled` on failure.
*   **Status:** Rejected
*   **Reason:** It addresses the symptom rather than the root cause. Kernel-level networking is inherently more robust and efficient.

### 2. Host Networking for all components
*   **Description:** Use `--net=host` for everything to simplify discovery.
*   **Status:** Rejected
*   **Reason:** Violates the principle of least privilege. Exposes containers to the local LAN and increases the attack surface of the host network.

## Consequences

### Positive
*   **Improved Recovery:** Remote sessions automatically reconnect once the host network is restored after sleep.
*   **Zero LAN Exposure:** Loopback binding (`127.0.0.1`) ensures that no one on the same WiFi/LAN can reach the containers.
*   **Network Isolation:** Bridge mode prevents the container from seeing or interfering with other host network traffic.
*   **Better Performance:** Native kernel-space networking has lower CPU overhead than userspace netstack.

### Negative
*   **Hard Dependency on TUN:** Containers will fail to start in remote mode if `/dev/net/tun` is missing. This is acceptable as the CLI already enforces this for remote sessions.

## Security & Risk Analysis

The transition to Kernel TUN mode requires elevated networking privileges, but the overall security posture of the project is **improved**.

| Feature | Old State (Userspace + Host) | New State (Kernel TUN + Bridge) |
| :--- | :--- | :--- |
| **LAN Exposure** | **High** (Accessible via Local IP) | **Zero** (Locked to 127.0.0.1) |
| **Host Network Visibility** | **Total** (Shares host interfaces) | **Isolated** (Private Bridge) |
| **Remote Reliability** | Brittle (Fails after Sleep) | **Robust** (Native Kernel recovery) |

### Risk Assessment
*   **Privilege Escalation:** While `NET_ADMIN` is an elevated capability, it is restricted to the container's network namespace. It does **not** grant the ability to escape the container or access the host filesystem.
*   **Comparison to DooD:** The risk posed by these networking privileges is significantly **lower** than the existing risk of **Docker-out-of-Docker (`/var/run/docker.sock`)**, which provides a direct path to host root access.
*   **Network Interference:** Because we use Bridge mode, a compromised container cannot modify the host's primary physical network interfaces (e.g., eth0, wlan0).

### Recommendation
Users requiring maximum security isolation should run the container in **Sandbox Mode** (passing `--no-docker` and avoiding `--remote`). For standard development usage, the combination of Kernel TUN and Loopback Binding provides the best balance of professional-grade reliability and local network security.
