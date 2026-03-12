# Step 4: VPN Sidecar Image

## Goal
Create a lightweight VPN connectivity provider with automatic cleanup.

## Files to Modify
- `images/gemini-vpn/Dockerfile`
- `images/gemini-vpn/docker-entrypoint.sh`
- `docker-bake.hcl`

## Technical Specification
1.  **Dockerfile:**
    - Base: `tailscale/tailscale:stable`.
    - Install `procps` if missing.
    - Copy the custom entrypoint.
2.  **Entrypoint Watchdog:**
    - Implement a while-loop: `while [ -d /proc/1 ]; do sleep 5; done`.
    - Once PID 1 (shared with parent session) exits, the watchdog must kill `tailscaled` to terminate the container.
    - Log: `">> [VPN] Parent session exited. Terminating sidecar..."`
3.  **Docker Bake:**
    - Add `gemini-vpn` target to `docker-bake.hcl`.
    - Use inheritance from `base` if possible, but the Tailscale image is preferred.

## Validation
- **Bash Test:** `tests/bash/test_sidecar_watchdog.bats`
- Launch a parent container with `--pid container:ID`.
- Verify the sidecar starts.
- Kill the parent and verify the sidecar exits within 10 seconds.
