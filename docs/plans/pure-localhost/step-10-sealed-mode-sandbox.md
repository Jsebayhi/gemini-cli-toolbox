# Step 10: Sealed Mode Sandbox

## 🎯 The Goal
Provide a "Maximum Security" execution mode for untrusted tasks.

## 💡 The "Why" (Technical Rationale)
For high-risk tasks, users need a way to "seal" the container. By implementing a single flag that disables all host integrations (Docker, IDE, and Network), we provide a foolproof security sandbox.

## 📝 The "What" (Action Plan)
Implement a new "macro" flag in the `gemini-toolbox` wrapper script that enforces multiple security restrictions.

## 📁 Files to Modify
- `bin/gemini-toolbox`
- `completions/gemini-toolbox.bash`

## 🛠️ The "How" (Technical Specification)

### 1. New Flag `--sealed`:
- When `--sealed` is detected:
    - `enable_docker=false`
    - `enable_vscode_integration=false`
    - `localhost_access=false`

### 2. Isolation Logic:
- Sealed session has NO Docker access, NO VS Code connectivity, NO local port mapping.
- **Exception:** VPN connectivity (Tier 2) is still allowed if explicitly requested.

### 3. Conflict Handling:
- If `--sealed` and `--network-host` both passed, exit with error.

## ✅ Validation
- **Test:** Run `gemini-toolbox --sealed --detached`.
- **Action:** Exec into container.
- **Verify:** `ls /var/run/docker.sock` fails.
- **Verify:** No IDE variables in `env`.
- **Verify:** Container shows no port mappings on host.
