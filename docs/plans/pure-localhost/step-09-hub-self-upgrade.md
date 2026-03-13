# Step 9: Hub Self-Upgrade

## 🎯 The Goal
Provide remote access to the Hub itself using its own connectivity tiers.

## 💡 The "Why" (Technical Rationale)
The Hub is the "Home Page" for your sessions. If a user is on a train and wants to launch a new task, they need to reach the Hub first. By allowing the Hub to attach a VPN sidecar to itself, we make the dashboard accessible from any device.

## 📝 The "What" (Action Plan)
Implement sidecar management subcommands for the Hub's wrapper script and add UI controls for its own connectivity.

## 📁 Files to Modify
- `bin/gemini-hub`
- `completions/gemini-hub.bash`
- `images/gemini-hub/app/templates/index.html`
- `images/gemini-hub/app/static/js/main.js`

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-hub` Subcommands:
- **`vpn-add` / `vpn-stop` / `vpn-restart`:** 
    - Same logic as `gemini-toolbox` sidecar management, hardcoded to target `gemini-hub-service`.
    - Sidecar name MUST be `gemini-hub-service-vpn`.

### 2. Autocompletion (`completions/gemini-hub.bash`):
- Update to support `vpn-add`, `vpn-stop`, and `vpn-restart` commands.

### 3. Hub Dashboard UI (`index.html` & `main.js`):
- **Header Actions:** Add a small toggle button in the Hub header:
    - If Hub VPN is OFF: Show `🌐 Add Remote Access`.
    - If Hub VPN is ON: Show `🌐 Public` (Active).
- **JavaScript Action:** 
    - Trigger `POST /api/vpn/[add|stop]` for `gemini-hub-service`.

## ✅ Validation
- **BATS Test:** `tests/bash/test_hub_self_upgrade.bats`
- Run `gemini-hub --no-vpn --detach`.
- Run `gemini-hub vpn-add`.
- Verify a `gemini-hub-service-vpn` sidecar is running on the host.
- Verify access via Tailscale hostname.
