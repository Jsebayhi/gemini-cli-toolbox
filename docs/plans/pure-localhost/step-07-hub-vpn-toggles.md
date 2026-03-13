# Step 7: Hub VPN Toggles (API & UI)

## 🎯 The Goal
Make the "Tiered Connectivity" model accessible through the web dashboard.

## 💡 The "Why" (Technical Rationale)
The power of modular networking is maximized when users can manage it without typing CLI commands. By adding VPN toggles directly to session cards, we enable users to "Go Remote" or "Go Dark" with a single click.

## 📝 The "What" (Action Plan)
Update the Hub backend to expose tier management API endpoints and update the frontend UI to use them.

## 📁 Files to Modify
- `images/gemini-hub/app/api/routes.py`
- `images/gemini-hub/app/services/launcher.py`
- `images/gemini-hub/app/templates/index.html`
- `images/gemini-hub/app/static/js/main.js`

## 🛠️ The "How" (Technical Specification)

### 1. Flask API (`images/gemini-hub/app/api/routes.py`):
- **Endpoint `POST /api/vpn/add`:** Takes `session_id`. Calls `gemini-toolbox vpn-add session_id`.
- **Endpoint `POST /api/vpn/stop`:** Takes `session_id`. Calls `gemini-toolbox vpn-stop session_id`.

### 2. UI Updates (`index.html` & `main.js`):
- **Session Card:** Add a new button in the card footer:
    - If `vpn` tier is NOT present: Show `🌐 +VPN`.
    - If `vpn` tier IS present: Show `🌐 VPN`.
- **JavaScript Action:** 
    - Trigger corresponding API call.
    - Show "spinner" while pending.
    - Refresh session list after success.

## ✅ Validation
- **Test:** Open Hub dashboard.
- **Action:** Click `+VPN` on a running session. 
- **Verify:** Card UI shows loader, then `VPN` badge appears.
- **Action:** Click active `VPN` button.
- **Verify:** Badge disappears, VPN sidecar is stopped.
