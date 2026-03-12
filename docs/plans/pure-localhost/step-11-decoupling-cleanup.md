# Step 11: Decoupling Cleanup

## 🎯 The Goal
Finalize the modular architecture and reduce the image footprint.

## 💡 The "Why" (Technical Rationale)
The main value of a sidecar architecture is the ability to specialize your containers. Now that VPN connectivity is handled by a dedicated image (`gemini-vpn`), there is NO reason to keep networking tools like `tailscale`, `iptables`, or `iproute2` in the `gemini-base` or `gemini-cli` images. Removing them makes the agent's environment cleaner, smaller, and more secure by reducing the number of "attack vectors" available to potential exploits.

## 📝 The "What" (Action Plan)
You must surgically remove all legacy networking dependencies from the base Dockerfiles and finalize the project documentation.

## 🛠️ The "How" (Technical Specification)

### 1. `images/gemini-base/Dockerfile` Cleanup:
- **Surgical Removal:** Find the `apt-get install` block and DELETE:
    - `tailscale`
    - `iptables`
    - `iproute2`
- **Result:** The base image MUST no longer contain any VPN-related software.

### 2. Documentation Finalization:
- **ADR Review:** Mark ADR-0057, ADR-0058, and ADR-0059 as "Accepted."
- **Root README:** Update the "Networking" section of `README.md` to explain the 2-tier architecture (Localhost vs. VPN sidecar).
- **Component GEMINI.md:** Update `images/gemini-cli/GEMINI.md` to reflect that Tailscale has been removed and connectivity is now managed via sidecars.

### 3. Final Build:
- Run `make clean` (to clear cache) and then `make build` to build the new, leaner images.
- Verify image size reduction (should be >10MB smaller).

## ✅ Validation
- **Full CI:** Run `make local-ci`.
- **Test:** Exec into a `cli` container.
- **Verify:** `tailscale --version` -> Should return "Command not found."
- **Verify:** `iptables -L` -> Should return "Command not found."
