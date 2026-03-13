# Step 4: VPN Sidecar Image

## 🎯 The Goal
Create a modular "Network Tier" image with built-in lifecycle synchronization.

## 💡 The "Why" (Technical Rationale)
By moving the VPN into its own sidecar, we decouple network infrastructure from application logic. The sidecar MUST be ephemeral: if the parent Gemini session dies, the VPN sidecar MUST die immediately to avoid "zombie" nodes that waste resources.

## 📝 The "What" (Action Plan)
Create a new Docker component (`images/gemini-vpn`) that acts as a specialized VPN provider.

## 📁 Files to Modify
- `images/gemini-vpn/Dockerfile`
- `images/gemini-vpn/docker-entrypoint.sh`
- `docker-bake.hcl`
- `Makefile` (Root)

## 🛠️ The "How" (Technical Specification)

### 1. `images/gemini-vpn/Dockerfile`:
- **Base:** `tailscale/tailscale:stable`.
- **Tools:** Install `procps` for `pkill`.
- **Standardization:** Add a `docker-entrypoint.sh`.

### 2. `images/gemini-vpn/docker-entrypoint.sh` (The Watchdog):
- **Mechanism:** Shares the parent's PID namespace. PID 1 is the parent's entrypoint.
- **The Watchdog Loop:** 
    - `while [ -d /proc/1 ]; do sleep 5; done`.
    - Once PID 1 is gone, `pkill tailscaled`.
- **Standardized Logging:** All logs start with `>> [VPN]`.

### 3. Build Orchestration:
- Register `gemini-vpn` in `docker-bake.hcl`.
- Add `build-vpn` target to the root `Makefile`.

## ✅ Validation
- **Test:** Run parent `docker run --rm -d --name parent busybox sleep 100`.
- **Test:** Launch sidecar `docker run --rm -d --name sidecar --pid container:parent gemini-vpn`.
- **Action:** Stop parent.
- **Verify:** Sidecar container exits automatically within 10 seconds.
