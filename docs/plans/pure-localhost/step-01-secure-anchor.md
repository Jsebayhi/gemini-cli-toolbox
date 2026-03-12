# Step 1: Secure Anchor (Networking Refactor)

## 🎯 The Goal
Shift the entire toolbox from "Open by Default" (host networking) to "Protected by Default" (bridge isolation).

## 💡 The "Why" (Technical Rationale)
Currently, using `--net=host` exposes all internal container ports to all network interfaces on the host machine. If a user is on a public Wi-Fi or a permissive corporate LAN, their Gemini session (port 3000) could be reachable by anyone on the same network. By switching to `bridge` mode and binding strictly to `127.0.0.1`, we create a "Secure Anchor" that is only reachable from the user's desktop, regardless of their network environment.

## 📝 The "What" (Action Plan)
You must modify the primary wrapper scripts to enforce bridge networking and loopback port mapping.

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-toolbox` Changes:
- **Variable Update:** Change the default value of `network_mode` from `--net=host` to `--network=bridge`.
- **Default Port Mapping:** 
    - Always append `-p 127.0.0.1:0:3000` to the `extra_docker_args` array.
    - **Note:** The `0` in `127.0.0.1:0:3000` tells Docker to pick a random available port on the host. This prevents collisions between multiple sessions.
- **New Flags:**
    - `--no-vpn`: A semantic flag that confirms the user wants to run without Tailscale. It sets `localhost_mode=true` and prevents any VPN-related warnings.
    - `--no-localhost`: Disables the default port mapping. Set `localhost_access=false` and skip the `-p` argument.
    - `--network-host`: A "legacy" escape hatch. Sets `raw_host=true`, reverts to `--net=host`, and MUST log a warning: `">> Warning: --network-host overrides --no-vpn/--remote isolation."`

### 2. `bin/gemini-hub` Changes:
- **Default Port Mapping:** Enforce `-p 127.0.0.1:8888:8888` for the Hub.
- **New Flag:**
    - `--no-vpn`: Makes the `TAILSCALE_KEY` requirement optional.

### 3. Conflict Resolution:
- If a user passes `--remote` (which implies VPN) AND `--no-vpn`, the script MUST exit with an error: `"Error: --remote and --no-vpn are incompatible."`

## ✅ Validation
- **Test:** Run `gemini-toolbox --no-vpn --detached`. 
- **Verify:** Run `docker ps` and ensure the container shows `127.0.0.1:XXXXX->3000/tcp`.
- **Verify:** Attempt to reach port 3000 via the host's LAN IP; it should be refused.
