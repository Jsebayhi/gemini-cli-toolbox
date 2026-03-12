# Step 3: Hub Local UI (Frontend)

## 🎯 The Goal
Communicate connectivity tiers clearly in the Hub dashboard and prioritize the fastest connection.

## 💡 The "Why" (Technical Rationale)
A "Localhost Hub" is useless if it still points users to Tailscale IPs when they are on the same machine. Localhost access is faster (lower latency) and more reliable (no VPN needed). We need to clearly label these "Local Only" or "Hybrid" sessions and ensure that when a user clicks "Open," they are taken to the local endpoint if it's reachable.

## 📝 The "What" (Action Plan)
You must update the Hub's HTML template and its main JavaScript logic to handle multiple connectivity endpoints.

## 🛠️ The "How" (Technical Specification)

### 1. UI Badge (Template):
- In the session card template (`index.html`), add a new badge element:
  - `{% if m.local_url %}<span class="badge local">LOCAL</span>{% endif %}`.
- Style it in `style.css` with a distinct look (e.g., green background, white text).

### 2. Smart Connection (JavaScript):
- In `main.js`, update the session link construction.
- **Logic:**
    - If `local_url` is present in the session data, use it as the `href` for the "Open" button.
    - If ONLY a Tailscale IP is available, use the VPN URL.
    - **Advanced:** Implement a simple "Local Reachability" check. When the page loads, try to fetch a dummy resource (e.g., a 1x1 pixel) from `localhost`. If it fails (meaning the user is likely on mobile), hide the `LOCAL` badge and fallback to the VPN IP even for hybrid sessions.

### 3. Badge Visibility:
- Add a CSS class `.hidden { display: none; }` to the local badge by default.
- Let the JavaScript reveal it if the reachability check passes.

## ✅ Validation
- **Test:** Open the Hub from your desktop.
- **Verify:** Local sessions show the `LOCAL` badge and link to `http://localhost:XXXX`.
- **Verify:** Open the Hub from your phone (via VPN). 
- **Verify:** The `LOCAL` badge should be hidden, and sessions should link to their Tailscale IPs.
