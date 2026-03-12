# Step 9: Hub Self-Upgrade

## 🎯 The Goal
Provide remote access to the Hub itself using its own connectivity tiers.

## 💡 The "Why" (Technical Rationale)
The Gemini Hub is the "Home Page" for your agent sessions. If a user is on a train and wants to launch a new task, they need to reach the Hub first. By allowing the Hub to attach a VPN sidecar to its own container, we make the dashboard accessible from any device on the Tailnet. This "Self-Upgrade" completes the autonomous management story.

## 📝 The "What" (Action Plan)
You must implement sidecar management subcommands for the Hub's wrapper script and add UI controls for its own connectivity.

## 🛠️ The "How" (Technical Specification)

### 1. `bin/gemini-hub` Subcommands:
- **`vpn-add` / `vpn-stop` / `vpn-restart`:** 
    - Same logic as `gemini-toolbox` sidecar management, but hardcoded to target the `gemini-hub-service` container name.
    - Sidecar name MUST be `gemini-hub-service-vpn`.

### 2. Hub Dashboard UI (`index.html` & `main.js`):
- **Header Actions:** In the Hub's top navigation bar (where the logo/version is), add a small toggle button:
    - If Hub VPN is OFF: Show `🌐 Add Remote Access`.
    - If Hub VPN is ON: Show `🌐 Public` (Active).
- **JavaScript Action:** 
    - Clicking the button MUST trigger the `POST /api/vpn/[add|stop]` endpoint with the hardcoded session ID `gemini-hub-service`.

## ✅ Validation
- **Test:** Start the Hub locally with `gemini-hub --no-vpn --detach`.
- **Action:** Open the dashboard at `http://localhost:8888`. 
- **Action:** Click `🌐 Add Remote Access`.
- **Verify:** Confirm that a `gemini-hub-service-vpn` sidecar is running on the host.
- **Verify:** Access the Hub dashboard from your phone via its Tailscale hostname (e.g., `http://gemini-hub-service:8888`).
