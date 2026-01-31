# 6. Remote Access Security Strategy

Date: 2026-01-08 (Updated: 2026-01-21)

## Status

Accepted

## Context

The user intends to access the Gemini CLI agent remotely (e.g., from a mobile phone) to assign tasks while on the move. This shifts the operational model from a "Local Development Tool" to a "Networked Service," introducing significant security risks.

We evaluated two main approaches to securing this access:

1.  **Container Hardening (Defense in Depth):**
    *   Attempting to restrict what the process can do if compromised.
    *   Techniques: Running as a non-privileged user, Read-Only file systems, blocking dependency installation (`pip`), dropping network capabilities.
    *   *Problem:* This severely degrades the utility of the agent. A development agent *needs* to write code, install libraries, and execute scripts to be useful. Furthermore, blocking `pip` or global writes is ineffective if the attacker owns the workspace (UID 1000) and can simply download/execute binaries locally.

2.  **Network Isolation (Zero Trust / VPN):**
    *   Keeping the container "soft" and fully featured but making it invisible to the public internet.
    *   Techniques: VPNs (Tailscale, WireGuard), Authenticated Proxies (Cloudflare Access).

## Decision

We explicitly **REJECT** the strategy of hardening the container internals for the purpose of remote security.
We **ADOPT** the strategy of **Network Isolation** via VPN (Virtual Private Network).

**The Container shall remain:**
*   **Privileged (UID 1000):** To ensure seamless file ownership and git operations.
*   **Writable:** To allow code generation, refactoring, and dependency management.
*   **Networked:** To allow the agent to fetch documentation and libraries.

**The Security Boundary is the Network:**
*   The service **MUST NOT** be exposed directly to the public internet (no port forwarding).
*   Remote access **MUST** be mediated by a secure transport layer (e.g., Tailscale, WireGuard).

## Update: Implementation Strategy (2026-01-21)

To operationalize the "Network Isolation" decision, we faced a choice on *where* the VPN endpoint should reside: on the Host or inside the Container.

We evaluated this against user constraints:
1.  **Zero Host Setup:** Ideally, the solution should live entirely within the container ecosystem.
2.  **Conflict Free:** Must operate correctly even if the host is connected to a corporate VPN.
3.  **Seamless Transition:** Ideally allows switching between "Desk Mode" (VS Code) and "Mobile Mode" (VPN) without restarting.

### Decision: Hybrid Strategy

We adopt a **Hybrid Strategy** that supports two distinct modes of operation, allowing the user to choose the trade-off that fits their current context.

#### 1. Host-Mediated Mode (Seamless)
*   **Mechanism:** The user installs a VPN (e.g., Tailscale) directly on the **Host OS**.
*   **Docker Config:** The container continues to run with `--net=host`.
*   **Pros:**
    *   **Seamless:** The container is accessible via `localhost` (for VS Code) and the Host's VPN IP (for Mobile) simultaneously. No session restart required.
    *   **Performance:** Native network speeds.
*   **Cons:**
    *   **Host Setup:** Requires installing software on the host.
    *   **VPN Conflicts:** May conflict if the host is already connected to a strict Corporate VPN.

#### 2. Container-Encapsulated Mode (Portable)
*   **Mechanism:** The VPN client (Tailscale) is embedded **inside the Docker image**.
*   **Activation:** Triggered via a flag (`--remote <key>`) or environment variable (`GEMINI_REMOTE_KEY`).
*   **Docker Config:** When active, the container switches from `--net=host` to **Bridge Mode** (`--network=bridge`) with explicit capability grants (`--cap-add=NET_ADMIN`, `--device /dev/net/tun`).
*   **Pros:**
    *   **Zero Host Setup:** Works on any machine with Docker.
    *   **Isolation:** Bypasses host network configurations (e.g., Corporate VPNs), ensuring connectivity.
*   **Cons:**
    *   **Exclusive Mode:** Because we drop `--net=host` to isolate the network stack, **VS Code Integration is disabled** in this mode.
    *   **Restart Required:** Switching from "VS Code Mode" to "VPN Mode" requires a container restart.

## Implementation Details (Container Mode)

**The Container shall:**
*   Include the `tailscale` binary in the base image.
*   Check for `TAILSCALE_AUTH_KEY` (or similar) at runtime.
*   If present, start `tailscaled` in userspace or tun mode.
*   **Identity Management:** To prevent collisions when running multiple containers simultaneously, the container must register with a unique, predictable hostname:
    *   Format: `gemini-<project_slug>-<suffix>`
    *   `project_slug`: Sanitized basename of the workspace (e.g., `my-project`).
    *   `suffix`: Short hash (first 4 chars of container ID) to allow multiple instances of the same project.
    *   The node shall be marked as `--ephemeral` to auto-cleanup the mesh dashboard on exit.

**The Wrapper Script (`gemini-toolbox`) shall:**
*   Detect if Remote Mode is requested.
*   **IF Remote:**
    *   Disable `--net=host`.
    *   Inject `TAILSCALE_AUTH_KEY`.
    *   Add `--cap-add=NET_ADMIN` and `--device /dev/net/tun`.
    *   Disable VS Code integration variables.
*   **ELSE (Default):**
    *   Keep `--net=host` (enabling Host-Mediated Mode if the user has it setup).

## Consequences

### Positive
*   **Usability:** The agent remains a powerful, frictionless development tool. It is not artificially restricted by "hardened" container settings.
*   **Flexibility:** Users can choose between "Zero Setup / Isolated" (Container Mode) or "Seamless / Integrated" (Host Mode) depending on their technical environment.
*   **Security:** The attack surface is reduced from "The entire Internet" to "Holders of the private VPN key."
*   **Simplicity:** No complex permission management inside Docker. The security boundary is clear (the network).

### Negative
*   **Dependency:** Requires the user to rely on a VPN solution (Tailscale).
*   **Integration Loss (Container Mode):** Enabling the internal VPN forces the container into an isolated network mode, breaking "Localhost" integrations like the VS Code Companion extension.
*   **Residual Risk:** If a client device is physically compromised (e.g., a stolen unlocked phone), the attacker has full access to the development environment, including the ability to persist malware via Git hooks. This risk is accepted as inherent to personal remote development.
