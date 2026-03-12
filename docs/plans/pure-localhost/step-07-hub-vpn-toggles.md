# Step 7: Hub VPN Toggles (API & UI)

## Goal
Provide a user-friendly dashboard for managing connectivity tiers.

## Files to Modify
- `images/gemini-hub/app/api/routes.py`
- `images/gemini-hub/app/services/launcher.py`
- `images/gemini-hub/app/templates/index.html`
- `images/gemini-hub/app/static/js/main.js`

## Technical Specification
1.  **API Routes:**
    - `POST /api/vpn/add`: Takes `session_id`. Calls `gemini-toolbox vpn-add session_id`.
    - `POST /api/vpn/stop`: Takes `session_id`. Calls `gemini-toolbox vpn-stop session_id`.
2.  **Service Integration:**
    - `LauncherService` MUST expose `vpn_add` and `vpn_stop` methods.
3.  **UI Components:**
    - On each session card, add a toggle button: 
        - If VPN is OFF: Show `🌐 +VPN` (Clicking adds sidecar).
        - If VPN is ON: Show `🌐 VPN` (Clicking stops sidecar).
    - Style the button to reflect active state.
4.  **Wait Indicators:** 
    - Display a loader on the card while the sidecar is being attached/detached.

## Validation
- **UI Test:** `images/gemini-hub/tests/ui/test_vpn_toggles.py`
- Mock `/api/vpn/add` and verify the UI updates correctly after clicking.
