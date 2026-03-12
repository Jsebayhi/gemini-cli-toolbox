# Step 8: Bulk VPN Management

## 🎯 The Goal
Synchronize connectivity for multiple sessions with a single command.

## 💡 The "Why" (Technical Rationale)
Power users often have multiple project sessions running simultaneously. Manually clicking `+VPN` on each card is tedious. By implementing bulk connectivity commands, we provide a seamless "Home to Away" transition. Before leaving the office, a user can click "START ALL VPN" to ensure every active session is reachable from their laptop or phone during their commute.

## 📝 The "What" (Action Plan)
You must implement the `--all` argument for VPN commands and add global action buttons to the Hub dashboard.

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-toolbox` Changes:
- **`vpn-add --all`:** 
    - Scans all running `gem-` containers that do NOT already have a `-vpn` sidecar.
    - Launches a sidecar for each one in parallel (using `&`).
- **`vpn-stop --all`:** 
    - Identifies all running containers ending in `-vpn` and stops them.

### 2. Hub Dashboard UI (`index.html` & `main.js`):
- **Global Actions Bar:** At the top of the session list, add two new primary buttons:
    - `🌐 START ALL VPN` (Enabled if `TAILSCALE_KEY` exists).
    - `🌐 STOP ALL VPN`.
- **API Support:** Update the Hub API to support the `--all` argument by passing it through to the toolbox CLI.
- **UI Progress:** Show a global loading overlay while the bulk operation is in progress.

## ✅ Validation
- **Test:** Launch 3 local sessions with `gemini-toolbox --no-vpn --detached`.
- **Action:** Click `START ALL VPN` in the Hub. 
- **Verify:** Wait for completion. Confirm that `tailscale status` now lists 3 new nodes.
- **Action:** Click `STOP ALL VPN`.
- **Verify:** Confirm all 3 VPN sidecars are stopped.
