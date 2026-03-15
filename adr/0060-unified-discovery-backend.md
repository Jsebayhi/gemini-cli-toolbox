# ADR-0060: Unified Discovery Backend

## Status
Accepted (Implemented in Step 2 of Pure Localhost Evolution)

## Context
Historically, the Gemini Hub relied exclusively on `tailscale status` to discover active sessions. This created a hard dependency on the VPN: if a user launched a session in "Pure Localhost" mode (without a Tailscale key), the session existed on the local Docker daemon but was completely invisible to the Hub UI.

To support the transition to a "User-Choice" networking model where VPN is optional, the Hub must be able to detect and manage sessions regardless of their network topology.

## Decision
We refactored the Hub's discovery mechanism to use a "Unified Discovery Backend".

### 1. Provider-Based Orchestration
The monolithic `TailscaleService.parse_peers` was replaced by a `DiscoveryService` that orchestrates multiple independent `DiscoveryProvider` classes:
*   **DockerService:** Queries `docker ps` to find all containers matching the `gem-*` naming convention on the local host. This is the new primary "Source of Truth" for local sessions.
*   **TailscaleService:** Queries `tailscale status` to find peers in the Tailnet.

### 2. Merging and Priority
The `DiscoveryService` merges the results from all available providers:
*   If a session is found by Docker but not Tailscale, it is marked as `[LOCAL]`.
*   If a session is found by Tailscale but not Docker, it is marked as `[VPN]`.
*   If a session is found by both, it is a "Hybrid" session.
*   **Data Priority:** Local discovery data (specifically the `local_url` derived from host port mappings) takes precedence over remote data. This allows the Hub UI to prefer zero-latency `localhost` connections when the user is on the same machine as the container.

### 3. Decoupling and State
The `DiscoveryService` was refactored from a Singleton to a standard class instantiated per-request. This eliminates global state, drastically improves testability, and prevents caching issues where the Hub UI would display stale session data.

## Consequences
*   **Visibility:** "Pure Localhost" sessions are now fully visible and manageable within the Hub dashboard.
*   **Resilience:** If the Tailscale daemon crashes or the user logs out, the Hub still functions normally for local containers.
*   **Complexity:** The backend logic must now handle discrepancies between Docker and Tailscale states, merging them gracefully without crashing.
*   **Performance:** Discovery now requires spawning two subprocesses (`docker ps` and `tailscale status`), making an efficient, non-redundant querying strategy critical (addressed by removing the O(N^2) `get_session_by_name` helper).
