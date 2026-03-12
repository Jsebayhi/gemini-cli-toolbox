# Step 2: Hub Docker Discovery (Backend)

## Goal
Enable the Hub to identify running sessions without relying on Tailscale status.

## Files to Modify
- `images/gemini-hub/app/services/tailscale.py`

## Technical Specification
1.  **New Method `get_local_ports()`:**
    - Execute `docker ps --format "{{.Names}}|{{.Ports}}"`.
    - Filter for names starting with `gem-`.
    - Parse the `.Ports` field for `"->3000/tcp"`.
    - Extract the host port (e.g., from `127.0.0.1:32768->3000/tcp`, port is `32768`).
    - Return a dictionary: `{ "container_name": "http://localhost:PORT" }`.
2.  **Refactor `parse_peers()`:**
    - Fetch local ports first.
    - Fetch Tailscale status as before.
    - Merge results: 
        - If a container is in both, mark it as `hybrid` and use the local port as the priority `local_url`.
        - If a container is ONLY in `docker ps`, mark it as `local-only` and set `online=True`.
    - Ensure session metadata (project, type, uid) is parsed correctly from the container name even without a Tailscale IP.

## Validation
- **Unit Test:** `images/gemini-hub/tests/unit/test_unified_discovery.py`
- Mock `docker ps` output with multiple `gem-` containers.
- Verify `parse_peers()` correctly merges and attributes the right `local_url`.
