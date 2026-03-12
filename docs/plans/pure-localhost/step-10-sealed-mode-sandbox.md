# Step 10: Sealed Mode Sandbox

## Goal
Provide a "One-Click" maximum isolation mode.

## Files to Modify
- `bin/gemini-toolbox`
- `completions/gemini-toolbox.bash`

## Technical Specification
1.  **Flag Implementation:** 
    - Add `--sealed` to `bin/gemini-toolbox`.
2.  **Enforced Defaults:**
    - If `--sealed` is passed, the script MUST automatically set:
        - `enable_docker=false` (Removes `/var/run/docker.sock`).
        - `enable_vscode_integration=false` (Removes IDE environment variables).
        - `localhost_access=false` (Removes `-p` port mapping).
3.  **Conflict Handling:**
    - `--sealed` overrides `--remote` (disables localhost port but keeps VPN sidecar).
    - If `--sealed` and `--network-host` are both passed, exit with error: `"--sealed and --network-host are incompatible."`

## Validation
- **BATS Test:** `tests/bash/test_sealed_mode.bats`
- Verify a `--sealed` session has no mapped ports, no Docker socket, and no VS Code environment variables.
