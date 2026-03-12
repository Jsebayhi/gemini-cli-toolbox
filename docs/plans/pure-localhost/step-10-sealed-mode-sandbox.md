# Step 10: Sealed Mode Sandbox

## 🎯 The Goal
Provide a "Maximum Security" execution mode for untrusted tasks.

## 💡 The "Why" (Technical Rationale)
Gemini agents are powerful but could be exploited if they process malicious code or data. For high-risk tasks (like analyzing a mysterious script or running an untrusted build), users need a way to "seal" the container. By implementing a single flag that disables all host integrations (Docker, IDE, and Network), we provide a foolproof security sandbox that guarantees the agent cannot impact the host machine.

## 📝 The "What" (Action Plan)
You must implement a new "macro" flag in the `gemini-toolbox` wrapper script that enforces multiple security restrictions simultaneously.

## 🛠️ The "How" (Technical Specification)

### 1. New Flag `--sealed`:
- **Implementation in `bin/gemini-toolbox`:** 
    - When `--sealed` is detected, the script MUST automatically force:
        - `enable_docker=false` (Removes `/var/run/docker.sock` mount).
        - `enable_vscode_integration=false` (Removes VS Code environment variables).
        - `localhost_access=false` (Suppresses `-p` port mapping).
        - `sealed_mode=true` (Used for internal logic).

### 2. Isolation Logic:
- A sealed session MUST have:
    - NO Docker access.
    - NO VS Code connectivity.
    - NO local port mapping.
- **Exception:** VPN connectivity (Tier 2) is still allowed if explicitly requested (e.g., `--sealed --remote`), as it uses a sidecar and doesn't expose host resources. However, the `LOCAL` badge in the Hub MUST remain hidden for sealed sessions.

### 3. Conflict Handling:
- If `--sealed` and `--network-host` are both passed, the script MUST exit with an error: `"--sealed and --network-host are incompatible."`

## ✅ Validation
- **Test:** Run `gemini-toolbox --sealed --detached`.
- **Action:** Exec into the container: `docker exec -it <id> bash`.
- **Verify:** Run `ls /var/run/docker.sock` -> Should fail.
- **Verify:** Run `env | grep GEMINI` -> Should NOT show IDE variables.
- **Verify:** Run `docker ps` on host -> Container should NOT show any port mappings.
