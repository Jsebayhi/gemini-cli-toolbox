# Step 5: Toolbox Sidecar Orchestration

## Goal
Add manual sidecar management to the gemini-toolbox CLI.

## Files to Modify
- `bin/gemini-toolbox`
- `completions/gemini-toolbox.bash`

## Technical Specification
1.  **Commands:**
    - `vpn-add <id>`: Starts a `gemini-vpn` sidecar attached to `<id>`.
    - `vpn-stop <id>`: Stops and removes the `${id}-vpn` sidecar.
    - `vpn-prune`: Removes all sidecar containers with label `com.gemini.role=sidecar` whose parent is no longer running.
2.  **Naming Convention:**
    - Sidecar name MUST be `${PARENT_NAME}-vpn`.
3.  **Docker Arguments:**
    - Sidecars MUST use: `--network container:${PARENT_NAME}`, `--pid container:${PARENT_NAME}`, and `--cap-add=NET_ADMIN`.
    - Sidecars MUST have labels: `com.gemini.role=sidecar`, `com.gemini.parent=${PARENT_NAME}`, `com.gemini.sidecar.type=vpn`.
4.  **Auto-Auth:**
    - `vpn-add` MUST pass `TAILSCALE_AUTH_KEY` to the sidecar.
    - Immediately after `docker run`, it MUST execute `docker exec ${sid}-vpn tailscale up --authkey=${key} --hostname=${sid}`.

## Validation
- **BATS Test:** `tests/bash/test_toolbox_sidecar.bats`
- Verify `vpn-add` attaches a functional VPN sidecar to a running bridge-mode container.
