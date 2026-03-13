# Step 6: Refactor --remote

## 🎯 The Goal
Standardize session startup and eliminate legacy "fat" image behavior.

## 💡 The "Why" (Technical Rationale)
Having multiple ways to enable VPN (one for startup, one for on-demand) increases complexity and maintenance. By refactoring the existing `--remote` flag to use the sidecar model, we unify all networking into a single architecture. This allows us to remove Tailscale from the `gemini-cli` image entirely.

## 📝 The "What" (Action Plan)
Refactor the `--remote` flag in the wrapper script and clean up the CLI image's entrypoint.

## 📁 Files to Modify
- `bin/gemini-toolbox`
- `images/gemini-cli/docker-entrypoint.sh`

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-toolbox` Refactor:
- **Orchestration Flow:** When `--remote` is detected:
    - **Phase 1: Session Start.** Launch the main container (CLI or Bash) FIRST in bridge mode. If `--no-localhost` is NOT set, ensure the default loopback port mapping is applied.
    - **Phase 2: Sidecar Launch.** Immediately after the main container is successfully started, the script MUST call the equivalent of `vpn-add` in the background.
- **Detached Mode:** If `-d` is used, simply launch both and exit.
- **Interactive Mode:** Launch the VPN sidecar in the background and ensure it doesn't block the interactive TTY of the main session.

### 2. `images/gemini-cli/docker-entrypoint.sh` Cleanup:
- **Surgical Removal:** Delete any code that starts `tailscaled`, checks for `TAILSCALE_AUTH_KEY`, or handles VPN authentication.
- **Result:** The entrypoint SHOULD ONLY handle user switching (`gosu`) and launching the application (`ttyd` + `gemini`).

## ✅ Validation
- **Test:** Run `gemini-toolbox --remote mock-key --detached`.
- **Verify:** Use `docker ps` to ensure TWO containers are running: `gem-proj-cli-uid` AND `gem-proj-cli-uid-vpn`.
- **Verify:** The session MUST be reachable via `localhost:XXXX` (if allowed) AND via Tailscale.
