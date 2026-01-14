# 6. Remote Access Security Strategy

Date: 2026-01-08

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

## Consequences

### Positive
*   **Usability:** The agent remains a powerful, frictionless development tool.
*   **Simplicity:** No complex permission management or "jail" configurations inside Docker.
*   **Security:** Reduces the attack surface from "The entire Internet" to "Holders of the private VPN key."

### Negative
*   **Dependency:** Requires the user to set up and maintain a VPN solution on both the host and the client device.
*   **Residual Risk:** If a client device is physically compromised (stolen unlocked phone), the attacker has full access to the development environment, including the ability to persist malware via Git hooks. This risk is accepted as inherent to personal remote development.
