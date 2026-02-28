# ADR-0058: Connectivity Sidecar Architecture

## Status
Proposed (Supersedes ADR-0057)

## Context
Standard Docker containers cannot have their port mappings (`-p`) modified once they have started. In previous versions, enabling VPN access or sharing a session on the LAN required a full restart of the Gemini session, which interrupted long-running autonomous tasks. 

Furthermore, bundling Tailscale and networking utilities inside the primary `gemini-cli` image increased its size, complexity, and attack surface.

## Decision
We will adopt a modular "Network Tier" architecture using Sidecar containers. All connectivity beyond the initial secure anchor will be handled by secondary containers sharing the **Network** and **PID** namespaces of the parent session.

### 1. The Three Tiers of Connectivity

| Tier | Name | Target Scope | Mechanism | Location |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Localhost** | Host Desktop | `-p 127.0.0.1:{PORT}:3000` | **Parent Container** |
| **Tier 2** | **VPN** | Remote/Mobile | Tailscale Daemon | VPN Sidecar (`-vpn`) |
| **Tier 3** | **LAN** | Home Wi-Fi | Socat/Proxy | LAN Sidecar (`-lan`) |

### 2. "Protected by Default" Policy
For maximum security, the toolbox enforces a "Secure Anchor" policy:
*   **Default State:** All sessions start with **Tier 1 (Localhost)** enabled and all other tiers disabled.
*   **Isolation:** Use `--network=bridge`. By binding strictly to `127.0.0.1`, we ensure sessions are NEVER reachable via the LAN unless Tier 3 is explicitly added.
*   **Universal Application:** This policy applies to both the **Gemini Hub** and individual **Sessions**.

### 3. Why Tier 1 (Localhost) is NOT a Sidecar
Localhost access is the "Permanent Anchor" for the toolbox. We keep it on the parent container because:
1.  **Deterministic Lifecycle:** Localhost access must be available from the very second the container starts. Relying on a sidecar would introduce a startup race condition.
2.  **Zero Resource Overhead:** Native Docker port mapping has negligible overhead compared to a proxy sidecar.
3.  **Port Reclamation:** Ensures the host port is tied to the session's actual existence, avoiding "Port already in use" errors during rapid sidecar restarts.
4.  **Internal Availability:** Even if `--no-localhost` is used (preventing host mapping), the parent's internal port 3000 remains open *inside* its network namespace, allowing dynamic sidecars to forward traffic to it at any time.

### 4. Networking Possibility Matrix

| Hub Mode | Session Requested | VPN (Tier 2) | Localhost (Tier 1) | LAN Reachable | Resulting Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Localhost** | Local (Protected) | Off | **On** | No | Start Parent only |
| **Localhost** | VPN + Local | **On** | **On** | No | Start Parent + VPN Sidecar |
| **Localhost** | VPN Only | **On** | Off | No | Start Parent (`--no-localhost`) + VPN Sidecar |
| **VPN** | Local (Protected) | Off | **On** | No | Start Parent only |
| **VPN** | VPN + Local | **On** | **On** | No | Start Parent + VPN Sidecar |
| **Any** | LAN Share | Off | **On** | **Yes** | Add LAN Sidecar to active session |

### 5. Tier Details & Image Strategy

#### Tier 2: VPN Decoupling (`images/gemini-vpn`)
*   **Base:** `tailscale/tailscale`.
*   **Enhancements:** Adds the PID-1 watchdog and standardized `>> INFO` logging.
*   **Benefit:** VPN re-authentication or hangs can be fixed by restarting the sidecar without touching the Gemini session.

#### Tier 3: LAN Sharing (`images/gemini-lan`)
*   **Base:** `alpine` (minimal).
*   **Mechanism:** `socat TCP-LISTEN:3000,fork,reuseaddr TCP:localhost:3000`.
*   **Exposition:** The sidecar maps `-p 0.0.0.0:{PORT}:3000` to the host.
*   **Benefit:** Provides a "Kill Switch" for Wi-Fi exposure.

### 6. Lifecycle & Cleanup
To prevent orphaned sidecars, we implement a "Double-Grip" strategy using shared PID namespaces and a central pruning service. 
*   **See [ADR-0059: Sidecar Connectivity Lifecycle](0059-sidecar-connectivity-lifecycle.md)** for detailed technical mandates on synchronization and pruning.

### 7. Naming, Labels & Discovery
*   **Naming:** `gem-{PROJECT}-{TYPE}-{ID}-[vpn|lan]`
*   **Labels:**
    *   `com.gemini.role=sidecar`
    *   `com.gemini.parent={SESSION_NAME}` (e.g., `gem-myproj-cli-123`)
    *   `com.gemini.sidecar.type=[vpn|lan]`
*   **Parsing Impact:** Since our standard parsing logic extracts metadata by splitting the hostname by `-` from the right (expecting index -1 to be the UID), the addition of `-vpn` or `-lan` suffixes would break this logic. Therefore, the Hub and CLI scripts must explicitly filter out or handle sidecar containers *before* attempting to parse their names for project/type metadata.
*   **Unified Discovery:** The Hub logic will merge `docker ps` (filtering for sidecar suffixes) with `tailscale status`.
    *   **First-Class Local Citizens:** Local containers found via `docker ps` are displayed as active sessions even if they lack a Tailscale IP (labeled as `[LOCAL ONLY]`).
    *   **Hybrid Discovery:** A Hub in localhost mode can still detect and launch VPN-enabled sessions if a key is provided, provided they are running on the local Docker daemon.

### 8. User Experience (UX) & Hub Launch Wizard
*   **Filtering:** `connect`, `stop`, and autocompletion scripts will explicitly ignore containers ending in `-vpn` or `-lan`.
*   **Command Parity:** 
    *   CLI: `gemini-toolbox [vpn|lan]-[add|stop] <id>`.
    *   Hub: UI buttons on session cards to toggle tiers.
*   **Adaptive Launch Wizard:**
    *   **Context Awareness:** If the Hub is running in Pure Localhost mode, the wizard defaults to launching sessions with Localhost access enabled.
    *   **Key Protection:** The "Enable VPN" toggle is only available if a Tailscale Auth Key is configured in the Hub.
    *   **Granular Control:** For VPN sessions, the wizard provides a toggle to disable Tier 1 (Localhost) access for strict remote-only scenarios.
*   **Hub Upgradeability:** The same architecture applies to the **Gemini Hub** itself. The Hub can be "upgraded" to VPN or LAN modes on-demand, spawning sidecars attached to its own container. If the Hub stops, its sidecars die automatically via Layer 1.
*   **Status Badges:** The Hub dashboard will show badges for every active tier: `[LOCAL] [VPN] [LAN]`.

### 9. Removal of Legacy Host Networking
The `net=host` (Raw Host Mode) is **deprecated and removed**. 
*   **Rationale:** `net=host` is insecure as it exposes all internal ports to all interfaces. 
*   **Replacement:** Users wanting LAN reachability must now use the Tier 3 LAN Sidecar, which provides the same reachability with better isolation and a dynamic lifecycle.

## Consequences
*   **Flexibility:** Precise, zero-downtime control over session visibility.
*   **Robustness:** Isolation of networking failures from application state.
*   **Security:** Removal of `iptables`, `iproute2`, and `tailscale` from the main CLI container.
*   **Complexity:** The `gemini-toolbox` script and Hub `LauncherService` must now orchestrate multiple containers.
