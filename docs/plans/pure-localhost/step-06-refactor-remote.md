# Step 6: Refactor --remote

## Goal
Update the legacy `--remote` flag to use the sidecar model.

## Files to Modify
- `bin/gemini-toolbox`
- `images/gemini-cli/docker-entrypoint.sh`

## Technical Specification
1.  **Orchestration Logic:**
    - When `--remote` is passed, the script MUST launch the main session container FIRST in bridge mode.
    - If detached, launch the main container and then immediately launch the VPN sidecar.
    - If interactive, launch the VPN sidecar in the background before or after starting the main container.
2.  **Removal of In-Container Tailscale:**
    - Remove `tailscaled` and all associated setup from the `gemini-cli` entrypoint.
    - The CLI image MUST no longer contain networking or Tailscale binaries.
3.  **Authentication:**
    - Use the `TAILSCALE_AUTH_KEY` provided via `--remote` or the environment to configure the sidecar.

## Validation
- **BATS Test:** `tests/bash/test_remote_refactor.bats`
- Verify `gemini-toolbox --remote mock-key` starts two separate containers.
- Verify the main container NO LONGER runs `tailscaled`.
