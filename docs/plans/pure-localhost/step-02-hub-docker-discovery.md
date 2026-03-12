# Step 2: Hub Docker Discovery (Backend)

## 🎯 The Goal
Unify session discovery by allowing the Hub to identify local containers directly via the Docker daemon.

## 💡 The "Why" (Technical Rationale)
The current Hub relies on Tailscale's "MagicDNS" and peer list for discovery. If a user is offline or doesn't have a Tailscale account, the Hub dashboard is empty, even if multiple local sessions are running. By querying the local Docker daemon, we make the Hub a first-class citizen for "Pure Localhost" mode, ensuring every running session is discoverable and manageable.

## 📝 The "What" (Action Plan)
You must refactor the Python service that provides the session list to include local containers.

## 🛠️ The "How" (Technical Specification)

### 1. `images/gemini-hub/app/services/tailscale.py` Changes:
- **New Method `get_local_ports()`:**
    - Execute `docker ps --format "{{.Names}}|{{.Ports}}"`.
    - Filter for names starting with `gem-`.
    - Parse the `.Ports` string. You are looking for a mapping to internal port 3000.
    - Example: `127.0.0.1:32768->3000/tcp` -> Extract `32768`.
    - Return a dictionary: `{ "container_name": "http://localhost:32768" }`.

### 2. `parse_peers()` Refactor:
- **Phase 1: Local Scan:** Call `get_local_ports()` first.
- **Phase 2: VPN Scan:** Call `tailscale status --json` as before.
- **Phase 3: Unified Merge:**
    - **Logic:**
        - If a session is in both lists (found via Docker name AND Tailscale IP), it's a "Hybrid" session. Mark it as `online=True` and use the local port mapping as its priority `local_url`.
        - If a session is ONLY in Docker (found via name, no matching Tailscale IP), it's a "Local Only" session. Mark it as `online=True` and set `local_url` as its primary endpoint.
        - If a session is ONLY in Tailscale (found via IP, no matching local container), it's a "Remote Session" (likely running on a different machine in the Tailnet). Mark it as `online=True` and set its IP as the primary endpoint.
- **Metadata Resilience:** The parsing logic MUST be able to extract the project name, session type (cli/bash), and UID solely from the container name if the Tailscale metadata is missing.

## ✅ Validation
- **Test:** Launch a session with `gemini-toolbox --no-vpn --detached`.
- **Verify:** Refresh the Hub dashboard (or use a `pytest` unit test) to ensure the session appears with its correct project name and local URL.
