# Step 9: Hub Self-Upgrade

## Goal
Enable remote access to the Hub dashboard itself.

## Files to Modify
- `bin/gemini-hub`
- `images/gemini-hub/app/services/launcher.py`

## Technical Specification
1.  **Hub CLI Support:**
    - `gemini-hub vpn-add`: Adds a sidecar to the `gemini-hub-service` container.
    - `gemini-hub vpn-stop`: Stops the `gemini-hub-service-vpn` sidecar.
2.  **Sidecar Upgrade Logic:**
    - Reuse the `vpn-add` logic from Step 5, but target the Hub's own container ID.
3.  **UI Feedback:**
    - Add a toggle in the Hub header to enable "Remote Access" for the dashboard itself.
    - Style the toggle to show "Public" vs "Local" status.

## Validation
- **BATS Test:** `tests/bash/test_hub_self_upgrade.bats`
- Run `gemini-hub --no-vpn`.
- Run `gemini-hub vpn-add`.
- Verify a sidecar is attached to the hub container.
