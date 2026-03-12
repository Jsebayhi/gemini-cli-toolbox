# Step 3: Hub Local UI (Frontend)

## Goal
Enable users to connect to local sessions via the dashboard dashboard.

## Files to Modify
- `images/gemini-hub/app/templates/index.html`
- `images/gemini-hub/app/static/js/main.js`

## Technical Specification
1.  **UI Badge:** 
    - In the session card template, add a badge: `{% if m.local_url %}<span class="badge local">LOCAL</span>{% endif %}`.
    - Style it with a green color to indicate local connectivity.
2.  **Smart Linking:**
    - In `main.js`, update the "Open" button href.
    - If `local_url` is present, use it as the primary link.
    - If `local_url` is absent, use the Tailscale IP as before.
3.  **Local Connection Check:**
    - Add logic to ping `localhost` from the browser (or use a simple image/fetch check) to confirm the user is actually on the host machine.
    - If localhost is unreachable (e.g., user is on mobile), hide the `LOCAL` badge and fallback to VPN.

## Validation
- **UI Test:** `images/gemini-hub/tests/ui/test_dashboard_local.py`
- Verify that a session with `local_url` but no Tailscale IP is displayed correctly and the link is clickable.
