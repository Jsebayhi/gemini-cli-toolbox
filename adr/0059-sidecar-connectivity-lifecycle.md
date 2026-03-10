# ADR-0059: Sidecar Connectivity Lifecycle

## Status
Proposed

## Context
Decoupling connectivity into sidecars introduces the risk of "Orphaned Containers"—sidecars that continue to run after their parent session has exited. This wastes system resources and can lead to naming collisions in subsequent runs.

## Decision
We will implement a "Double-Grip" strategy to ensure sidecars are cleaned up automatically and immediately.

### Layer 1: Synchronized PID Lifecycle (Active/Immediate)
All sidecar containers MUST share the **PID Namespace** of the parent session (`--pid container:{ID}`).

#### 1. The Watchdog Monitor
Every sidecar image (`gemini-vpn`, `gemini-lan`) features an entrypoint wrapper that runs a tiny watchdog process. 
*   **Logic:** `tail --pid=1 -f /dev/null`.
*   **How it works:** Because of the shared PID namespace, the sidecar sees the parent's entrypoint as PID 1. The `tail --pid=1` command waits for that specific process to exit.
*   **Benefit:** If the parent container stops, crashes, or is `docker kill`'d, the watchdog detects the death of PID 1 and terminates the sidecar process instantly.
*   **Compatibility:** Protocol-agnostic. It works for `gemini-cli` (web UI) and `bash` sessions (no web UI) identically.

### Layer 2: Hub Pruning Service (Passive/Safety Net)
The Gemini Hub `PruneService` acts as a global garbage collector. Because it is passive, it relies on the Hub running. Layer 1 remains the primary, immediate defense.

#### 1. Label-Based Discovery
The Hub periodically scans all local containers for the following label:
*   `com.gemini.role=sidecar`

#### 2. Relationship Verification
For every sidecar found, the Hub will:
1.  Read the `com.gemini.parent` label (which holds the exact container *name*).
2.  Attempt to `docker inspect` the parent name.
3.  If the parent does not exist or is not in a `running` state, the Hub executes `docker rm -f {SIDECAR_ID}`.

### 3. Implementation Parity (Hub & Sessions)
The same logic applies to the Gemini Hub itself. 
*   If the Hub is "upgraded" to VPN or LAN modes, it will spawn sidecars attached to its own container.
*   If the Hub container is stopped, its connectivity sidecars die automatically via Layer 1.

## Consequences
*   **Reliability:** Zero-lag cleanup ensures no lingering background processes.
*   **Security:** Prevents "zombie" VPN nodes from remaining connected to the mesh after a session ends.
*   **Constraint:** Sidecars cannot be started *before* the parent session is in a `created` or `running` state.
