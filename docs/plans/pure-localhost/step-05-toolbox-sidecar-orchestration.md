# Step 5: Toolbox Sidecar Orchestration

## 🎯 The Goal
Provide a command-line interface for dynamic, zero-downtime connectivity management.

## 💡 The "Why" (Technical Rationale)
Standard Docker port mappings cannot be modified after a container starts. Sidecars allow "attaching" network tiers (like VPN) to a running container without touching its main process. This makes the Gemini CLI "always-on" and globally available on-demand.

## 📝 The "What" (Action Plan)
Implement the `vpn-add`, `vpn-stop`, and `vpn-restart` subcommands in `bin/gemini-toolbox`.

## 📁 Files to Modify
- `bin/gemini-toolbox`
- `completions/gemini-toolbox.bash`

## 🛠️ The "How" (Technical Specification)

### 1. New Commands in `bin/gemini-toolbox`:
- **`vpn-add [id]`:** 
    - Scans for the target session's container ID.
    - **Safety Check:** If `${id}-vpn` already exists, it MUST stop it first before re-launching.
    - Launches a `gemini-vpn` sidecar with:
        - `--network container:${id}`
        - `--pid container:${id}`
        - `--cap-add=NET_ADMIN`
        - Labels: `com.gemini.role=sidecar`, `com.gemini.parent=${id}`, `com.gemini.sidecar.type=vpn`
    - **Authentication:** Pass `TAILSCALE_AUTH_KEY` as an environment variable (`-e`).
    - **Bootstrap:** Immediately execute `docker exec ${id}-vpn tailscale up --authkey=${key} --hostname=${id}` in a background process (or with a small sleep).
- **`vpn-stop [id]`:** 
    - Identifies and kills the sidecar: `docker stop ${id}-vpn`.
- **`vpn-restart [id]`:** 
    - Wrapper: `vpn-stop` followed by `vpn-add`.
- **`vpn-prune`:** 
    - Cleanup command that finds all containers with label `com.gemini.role=sidecar` and removes any whose parent is NOT running.

### 2. Autocompletion:
- Update `completions/gemini-toolbox.bash` to include the new commands.
- **Filtering:** The autocompletions for `stop` and `connect` MUST explicitly hide any container names ending in `-vpn`.

## ✅ Validation
- **Test:** `gemini-toolbox vpn-add <running_session_id>`.
- **Verify:** `tailscale status` confirms the session has joined the Tailnet.
- **Test:** `gemini-toolbox vpn-restart <id>`.
- **Verify:** The sidecar is replaced and successfully re-authenticates.
