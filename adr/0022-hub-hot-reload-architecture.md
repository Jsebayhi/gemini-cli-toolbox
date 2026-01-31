# ADR 0011-DRAFT: Hub 'hot' reload Architecture

## Status
**DRAFT** - Open for Discussion

## Context
The current Gemini Hub acts as a singleton "Service". It runs on a fixed port (8888) and a fixed Tailscale hostname (`gemini-hub`).
Users often work across multiple independent workspace roots (e.g., `~/company-projects`, `~/personal-projects`).

Currently, if a user wants to switch contexts or add a new workspace root, they must kill the existing Hub and restart it with new arguments. This is disruptive and leads to "Docker conflict" errors if the cleanup isn't perfect.

We need to decide how to handle the need for different workspace views.

## Options Considered

### Option 1: Multi-Hub (Independent Instances)
Allow multiple Hub containers to run side-by-side.
*   `gemini-hub --name hub-work --workspace ~/work`
*   `gemini-hub --name hub-personal --workspace ~/personal`

*   **Pros:** Complete isolation.
*   **Cons:**
    *   **Port Conflicts:** Each Hub needs a unique port (8888, 8889...).
    *   **DNS Conflicts:** Each Hub needs a unique Tailscale hostname (`gemini-hub-work`, `gemini-hub-perso`).
    *   **Cognitive Load:** The user must remember which URL corresponds to which context.
    *   **Resource Heavy:** Multiple Python/Tailscale processes.

### Option 2: Singleton with "Hot Reload" (The Aggregator)
There is only one Hub, but it is mutable.
*   User runs: `gemini-hub --workspace ~/work` -> Starts Hub.
*   User runs: `gemini-hub --workspace ~/personal` -> **Detects running Hub, updates its config dynamically.**

*   **Pros:**
    *   One URL (`gemini-hub:8888`) for everything.
    *   Efficient resource usage.
    *   Seamless UX (no "Error: Address in use").
*   **Cons:**
    *   Requires adding an API to the Hub to accept config updates.
    *   Requires the Hub to dynamically update its internal `HUB_ROOTS` list without restarting.

### Option 3: Singleton with "Restart Prompt" (The Interrupter)
If the Hub is running, prompt the user to replace it.
*   `>> A Hub is already running with roots: /work`
*   `>> Do you want to stop it and start with: /personal? [y/N]`

*   **Pros:** Simple to implement (Bash logic). Explicit user intent.
*   **Cons:** Disruptive. You lose access to the previous context.

## Recommendation: Towards Option 2 (The Aggregator)

The Hub should ideally be a "Window into the Host". The Host sees all files; the Hub should be able to see whatever the user grants it access to.

**Proposed Workflow:**
1.  **Launch:** `gemini-hub --workspace ~/A` starts the server.
2.  **Add:** `gemini-hub --workspace ~/B` checks for existence.
    *   If running, it executes `docker exec gemini-hub-service update-config --add ~/B`.
    *   The Flask app updates its in-memory `HUB_ROOTS` list.
    *   The Docker container must have *all* potential parents mounted, OR we need to accept that we can only add paths that were covered by the initial Docker Volume mounts.

**Wait, The Volume Mount Problem:**
Docker volumes are immutable at runtime. We cannot mount `~/B` into a running container if it wasn't there at start.
*   *Correction:* If `~/A` and `~/B` are distinct trees, **Option 2 is impossible without a restart** because the container simply cannot read the files of `~/B`.

**Revised Recommendation: Option 3 (The Smart Restart)**
Since we cannot dynamically attach volumes, we must restart the container to change the view. We can make this seamless by recovering the previous state.

**Technical Implementation:**
1.  **Introspection:**
    *   Use `docker inspect` to retrieve the `HUB_ROOTS` and `HOST_CONFIG_ROOT` environment variables from the running `gemini-hub-service`.
2.  **Union Strategy:**
    *   Detect if the new requested workspace is already covered by the existing roots.
    *   If not, calculate a new set of roots: `New_Roots = Existing_Roots + Requested_Roots`.
3.  **User Interaction:**
    *   Prompt the user: "Merge (A+B) or Replace (B)?"
4.  **Execution:**
    *   `docker stop gemini-hub-service`
    *   `docker run ... -v A:/A -v B:/B ...`

This approach keeps the script stateless (no sidecar files) and robust.
