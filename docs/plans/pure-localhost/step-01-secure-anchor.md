# Step 1: Secure Anchor (Networking Refactor)

## Goal
Shift from insecure `--net=host` to bridge isolation by default.

## Files to Modify
- `bin/gemini-toolbox`
- `bin/gemini-hub`
- `completions/gemini-toolbox.bash`
- `completions/gemini-hub.bash`

## Technical Specification
1.  **Defaults:** Change `network_mode` default from `--net=host` to `--network=bridge`.
2.  **Port Mapping:**
    - `bin/gemini-toolbox`: Append `-p 127.0.0.1:0:3000` to `extra_docker_args` by default.
    - `bin/gemini-hub`: Append `-p 127.0.0.1:8888:8888` to `docker_run_args` by default.
3.  **New Flags:**
    - `--no-vpn`: Sets `localhost_mode=true`. Disables VPN startup logic.
    - `--no-localhost`: Sets `localhost_access=false`. Suppresses `-p` flag mapping.
    - `--network-host`: Sets `raw_host=true`. Reverts to `--net=host` and logs a warning: `"--network-host overrides --no-vpn/--remote isolation."`
4.  **Conflicts:**
    - If `--remote` AND `--no-vpn` are passed, exit with error: `"--remote and --no-vpn are incompatible."`
    - If `--remote` AND `--no-tmux` are passed, exit with error: `"--remote and --no-tmux are incompatible."`

## Validation
- **BATS Test:** `tests/bash/test_localhost_mode.bats`
- **Case 1:** `gemini-toolbox --no-vpn` -> Verify `docker run` contains `--network=bridge` and `-p 127.0.0.1:0:3000`.
- **Case 2:** `gemini-toolbox --network-host` -> Verify `docker run` contains `--net=host`.
- **Case 3:** `gemini-hub --no-vpn` -> Verify `docker run` contains `--network=bridge` and `-p 127.0.0.1:8888:8888`.
