# Step 11: Decoupling Cleanup

## 🎯 The Goal
Finalize the modular architecture and reduce the image footprint.

## 💡 The "Why" (Technical Rationale)
With VPN in its own sidecar, there is NO reason to keep `tailscale`, `iptables`, or `iproute2` in `gemini-base` or `gemini-cli`. Removing them makes the agent's environment cleaner, smaller, and more secure.

## 📝 The "What" (Action Plan)
Surgically remove all legacy networking dependencies from the base Dockerfiles and finalize the project documentation.

## 📁 Files to Modify
- `images/gemini-base/Dockerfile`
- `images/gemini-cli/Dockerfile`
- `README.md`
- `GEMINI.md` (Root)
- `images/gemini-cli/GEMINI.md`

## 🛠️ The "How" (Technical Specification)

### 1. `images/gemini-base/Dockerfile` Cleanup:
- **Surgical Removal:** DELETE `tailscale`, `iptables`, and `iproute2` from `apt-get install`.

### 2. Documentation Finalization:
- **ADR Review:** Mark ADR-0057, ADR-0058, ADR-0059 as "Accepted."
- **Root README:** Update "Networking" section to explain 2-tier architecture.
- **Component GEMINI.md:** Update to reflect Tailscale removal.

### 3. Final Build:
- Run `make build` and verify size reduction.

## ✅ Validation
- **Full CI:** `make local-ci`.
- **Test:** Exec into `cli` container.
- **Verify:** `tailscale --version` returns "Command not found."
