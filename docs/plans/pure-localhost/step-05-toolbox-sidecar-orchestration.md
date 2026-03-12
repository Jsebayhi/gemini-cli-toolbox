# Step 5: Toolbox Sidecar Orchestration

## 🎯 The Goal
Provide a command-line interface for dynamic, zero-downtime connectivity management.

## 💡 The "Why" (Technical Rationale)
Standard Docker port mappings cannot be modified after a container starts. This means that if a user starts a session locally but later wants to share it on a VPN, they would normally have to restart the session, losing their state and context. By using sidecar orchestration, we can "attach" or "detach" network tiers (like VPN) to a running container without touching its main process. This makes the Gemini CLI "always-on" and globally available on-demand.

## 📝 The "What" (Action Plan)
You must implement a suite of new subcommands in the `gemini-toolbox` wrapper script.

## 🛠️ The "How" (Technical Specification)

### 1. New Commands in `bin/gemini-toolbox`:
- **`vpn-add [id|--all]`:** 
    - Scans for the target session's container ID.
    - Launches a `gemini-vpn` sidecar with:
        - `--network container:${PARENT_NAME}`
        - `--pid container:${PARENT_NAME}`
        - `--cap-add=NET_ADMIN`
        - Labels: `com.gemini.role=sidecar`, `com.gemini.parent=${PARENT_NAME}`, `com.gemini.sidecar.type=vpn`
    - **Authentication:** Must pass `TAILSCALE_AUTH_KEY` as an environment variable to the sidecar.
    - **Bootstrap:** Immediately after `docker run`, it MUST execute `docker exec ${sid}-vpn tailscale up --authkey=${key} --hostname=${sid}`.
- **`vpn-stop [id|--all]`:** 
    - Identifies and kills the sidecar: `docker stop ${sid}-vpn`.
- **`vpn-restart [id|--all]`:** 
    - Simple wrapper: `vpn-stop` followed by `vpn-add`.
- **`vpn-prune`:** 
    - A cleanup command that finds all containers with the `com.gemini.role=sidecar` label and removes any whose "parent" container is no longer in a `running` state.

### 2. Autocompletion:
- Update `completions/gemini-toolbox.bash` to include the new commands.
- **Filtering:** The `connect` and `stop` autocompletions MUST explicitly hide containers ending in `-vpn` or `-lan` to prevent users from accidentally connecting to a network sidecar.

## ✅ Validation
- **Test:** Start a session with `gemini-toolbox --no-vpn --detached`.
- **Action:** Run `gemini-toolbox vpn-add`. 
- **Verify:** Use `tailscale status` to confirm the session has joined the Tailnet.
- **Action:** Run `gemini-toolbox vpn-stop`.
- **Verify:** Confirm the session is gone from the Tailnet but STILL running locally.
