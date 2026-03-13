# Step 8: Bulk VPN Management

## 🎯 The Goal
Synchronize connectivity for multiple sessions with a single command.

## 💡 The "Why" (Technical Rationale)
Power users often have multiple project sessions running. Manually clicking `+VPN` on each card is tedious. By implementing bulk connectivity commands, we provide a seamless "Home to Away" transition.

## 📝 The "What" (Action Plan)
Implement the `--all` argument for VPN commands and add global action buttons to the Hub dashboard.

## 📁 Files to Modify
- `bin/gemini-toolbox`
- `completions/gemini-toolbox.bash`
- `images/gemini-hub/app/api/routes.py`
- `images/gemini-hub/app/templates/index.html`
- `images/gemini-hub/app/static/js/main.js`

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-toolbox` Changes:
- **`vpn-add --all`:** 
    - Scans all running `gem-` containers that do NOT already have a `-vpn` sidecar.
    - Launches a sidecar for each one in parallel (using `&`).
- **`vpn-stop --all`:** 
    - Identifies all running containers ending in `-vpn` and stops them.
- **`vpn-restart --all`:**
    - Combined stop and add for all sessions.

### 2. Autocompletion (`completions/gemini-toolbox.bash`):
- Update to support `--all` as a valid argument for `vpn-add`, `vpn-stop`, and `vpn-restart`.

### 3. Hub Dashboard UI (`index.html` & `main.js`):
- **Global Actions Bar:** Add two primary buttons: `🌐 START ALL VPN` and `🌐 STOP ALL VPN`.
- **API Support:** Update Hub API to support `--all`.

## ✅ Validation
- **BATS Test:** `tests/bash/test_bulk_vpn.bats`
- Launch 3 local sessions.
- Run `vpn-add --all` and verify 3 sidecars are created.
- Run `vpn-stop --all` and verify all 3 are removed.
