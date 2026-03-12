# Step 8: Bulk VPN Management

## Goal
Efficiently synchronize connectivity for all active sessions.

## Files to Modify
- `bin/gemini-toolbox`
- `images/gemini-hub/app/templates/index.html`
- `images/gemini-hub/app/static/js/main.js`

## Technical Specification
1.  **CLI Bulk Support:**
    - `gemini-toolbox vpn-add --all`: Scans all `gem-` containers WITHOUT a `-vpn` sidecar and adds one to each.
    - `gemini-toolbox vpn-stop --all`: Stops all existing `-vpn` sidecar containers.
2.  **Dashboard Global Controls:**
    - Add two global buttons at the top of the session list: `START ALL VPN` and `STOP ALL VPN`.
    - These buttons trigger the bulk CLI commands via a new API endpoint.
3.  **UI Feedback:**
    - Show a global progress indicator while the bulk operation is running.

## Validation
- **BATS Test:** `tests/bash/test_bulk_vpn.bats`
- Launch 3 sessions.
- Run `vpn-add --all` and verify 3 sidecars are created.
- Run `vpn-stop --all` and verify all 3 are removed.
