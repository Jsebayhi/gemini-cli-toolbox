# Step 2: Hub Docker Discovery (Backend)

## 🎯 The Goal
Unify session discovery by allowing the Hub to identify local containers directly via the Docker daemon.

## 💡 The "Why" (Technical Rationale)
The current Hub relies on Tailscale's "MagicDNS" and peer list for discovery. If a user is offline or doesn't have a Tailscale account, the Hub dashboard is empty, even if multiple local sessions are running. By querying the local Docker daemon, we make the Hub a first-class citizen for "Pure Localhost" mode, ensuring every running session is discoverable and manageable.

## 📝 The "What" (Action Plan)
Refactor the Python service that provides the session list to include local containers and update the auto-shutdown monitor.

## 📁 Files to Modify
- `images/gemini-hub/app/services/tailscale.py`
- `images/gemini-hub/app/services/monitor.py`

## 🛠️ The "How" (Technical Specification)

### 1. `images/gemini-hub/app/services/tailscale.py` Changes:
- **`get_local_ports()`:**
    - Execute `docker ps --format "{{.Names}}|{{.Ports}}"`.
    - Filter for names starting with `gem-`.
    - Parse the `.Ports` field for `"->3000/tcp"`.
    - Extract the host port (e.g., `32768` from `127.0.0.1:32768->3000/tcp`).
    - Return a dictionary: `{ "container_name": "http://localhost:PORT" }`.
- **`parse_peers()` Refactor:**
    - Fetch local ports FIRST.
    - Fetch Tailscale status SECOND.
    - **Unified Merge:**
        - If a session is in both lists, mark it as `hybrid` and use the local port mapping as its priority `local_url`.
        - If a session is ONLY in Docker, mark it as `local-only` and set `online=True`.
    - **Metadata Parsing:** Use regex to extract metadata from the container name if Tailscale data is missing:
      - `^gem-(?P<project>.*)-(?P<type>[^-]*)-(?P<uid>[^-]*)$`.

### 2. Auto-Shutdown Monitor (`monitor.py`):
- **Filtering Logic:** When counting active sessions for the auto-shutdown timer (60s), the monitor MUST explicitly filter out containers ending in `-vpn`.
- **Reason:** To prevent double-counting and ensure the Hub shuts down correctly when no actual Gemini sessions are active.

## ✅ Validation
- **Unit Test:** `images/gemini-hub/tests/unit/test_unified_discovery.py`.
- **Verify:** `parse_peers()` correctly merges and attributes the right `local_url`.
- **Test:** Launch a session and its VPN sidecar.
- **Verify:** The Hub dashboard counts this as ONE session, not two.
