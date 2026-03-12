# Step 7: Hub VPN Toggles (API & UI)

## 🎯 The Goal
Make the "Tiered Connectivity" model accessible through the web dashboard.

## 💡 The "Why" (Technical Rationale)
The power of modular networking is maximized when users can manage it without typing complex CLI commands. By adding VPN toggles directly to the session cards in the Hub, we enable users to "Go Remote" (enable VPN) or "Go Dark" (stop VPN) for any session with a single click. This is especially useful for users who frequently move between home, office, and travel.

## 📝 The "What" (Action Plan)
You must update the Hub backend to expose tier management API endpoints and update the frontend UI to use them.

## 🛠️ The "How" (Technical Specification)

### 1. Flask API (`images/gemini-hub/app/api/routes.py`):
- **Endpoint `POST /api/vpn/add`:** 
    - Argument: `session_id`.
    - Action: Executes `gemini-toolbox vpn-add session_id`.
- **Endpoint `POST /api/vpn/stop`:** 
    - Argument: `session_id`.
    - Action: Executes `gemini-toolbox vpn-stop session_id`.
- **Launcher Integration:** Ensure the `LauncherService` class in `launcher.py` is updated to support these new subcommand executions.

### 2. UI Updates (`index.html` & `main.js`):
- **Session Card:** Add a new button in the card footer:
    - If `vpn` tier is NOT present in the session's `tiers` list: 
        - Show `🌐 +VPN` (Styling: Transparent/Dimmed).
    - If `vpn` tier IS present:
        - Show `🌐 VPN` (Styling: Solid Blue/Active).
- **JavaScript Action:** 
    - Clicking the button MUST trigger the corresponding API call.
    - While the call is pending, the card should show a "spinner" or "loading" state to prevent duplicate clicks.
    - Refresh the session list immediately after a successful action.

## ✅ Validation
- **Test:** Open the Hub dashboard.
- **Action:** Click `+VPN` on a running session. 
- **Verify:** The card UI should show a loader, and once finished, the `VPN` badge should appear alongside the `LOCAL` badge.
- **Action:** Click the active `VPN` button.
- **Verify:** The badge should disappear, and the VPN sidecar container should be stopped on the host.
