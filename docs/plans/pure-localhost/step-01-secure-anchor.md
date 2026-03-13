# Step 1: Secure Anchor (Networking Refactor)

## 🎯 The Goal
Shift the entire toolbox from "Open by Default" (host networking) to "Protected by Default" (bridge isolation).

## 💡 The "Why" (Technical Rationale)
Currently, using `--net=host` exposes all internal container ports to all network interfaces on the host machine. If a user is on a public Wi-Fi or a permissive corporate LAN, their Gemini session (port 3000) could be reachable by anyone on the same network. By switching to `bridge` mode and binding strictly to `127.0.0.1`, we create a "Secure Anchor" that is only reachable from the user's desktop, regardless of their network environment.

## 📝 The "What" (Action Plan)
Modify the primary wrapper scripts to enforce bridge networking and loopback port mapping, and update the CLI to capture the assigned port.

## 📁 Files to Modify
- `bin/gemini-toolbox`
- `bin/gemini-hub`
- `completions/gemini-toolbox.bash`
- `completions/gemini-hub.bash`
- `tests/bash/test_toolbox.bats` (Alignment)

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-toolbox` Changes:
- **Variable Update:** Around line 550, change `local network_mode="--net=host"` to `local network_mode="--network=bridge"`.
- **Default Port Mapping:** 
    - Initialize `local localhost_access=true`.
    - If `localhost_access` is true, append `-p 127.0.0.1:0:3000` to `extra_docker_args`.
    - **Note:** The `0` in `127.0.0.1:0:3000` tells Docker to pick a random available port.
- **Port Capture Logic:** 
    - After `docker run` (if detached), or during the "Info" printout:
    - Execute `docker inspect --format='{{(index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort}}' ${gemini_session_id}` to find the assigned host port.
    - Log: `">> Session available at http://localhost:${port}"`.
- **New Flags:**
    - `--no-vpn`: Sets `localhost_mode=true`. A semantic flag for offline use.
    - `--no-localhost`: Sets `localhost_access=false`. Suppresses the `-p` flag.
    - `--network-host`: Sets `raw_host=true`. Reverts to `--net=host` and logs a warning: `">> Warning: --network-host overrides --no-vpn/--remote isolation."`

### 2. `bin/gemini-hub` Changes:
- **Default Port Mapping:** Enforce `-p 127.0.0.1:8888:8888` for the Hub.
- **New Flag:**
    - `--no-vpn`: Makes the `TAILSCALE_KEY` requirement optional and disables Tailscale startup logic.

### 3. Conflict Resolution:
- If `--remote` AND `--no-vpn`, exit with: `"Error: --remote and --no-vpn are incompatible."`
- If `--remote` AND `--no-tmux`, exit with: `"Error: --remote and --no-tmux are incompatible."`

### 4. Test Alignment:
- Search `tests/bash/` for any tests using `assert_line --partial "--net=host"` and update them to expect `--network=bridge`.

## ✅ Validation
- **Test:** Run `gemini-toolbox --no-vpn --detached`. 
- **Verify:** `docker ps` shows mapping like `127.0.0.1:32768->3000/tcp`.
- **Verify:** The script successfully prints the `http://localhost:32768` URL.
