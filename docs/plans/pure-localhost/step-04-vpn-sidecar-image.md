# Step 4: VPN Sidecar Image

## 🎯 The Goal
Create a modular "Network Tier" image with built-in lifecycle synchronization.

## 💡 The "Why" (Technical Rationale)
Bundling VPN software inside the Gemini session container creates "Fat" images and prevents connectivity maintenance without restarting the session. By moving the VPN into its own sidecar, we decouple network infrastructure from application logic. The sidecar MUST be ephemeral: if the parent Gemini session dies, the VPN sidecar MUST die immediately to avoid "zombie" nodes that waste resources and can cause naming collisions in subsequent runs.

## 📝 The "What" (Action Plan)
You must create a new Docker component (`images/gemini-vpn`) that acts as a specialized VPN provider.

## 🛠️ The "How" (Technical Specification)

### 1. `images/gemini-vpn/Dockerfile`:
- **Base:** Use the official `tailscale/tailscale:stable` image.
- **Tools:** Install `procps` to ensure `pkill` and `ps` are available for the watchdog.
- **Standardization:** Add a `docker-entrypoint.sh`.

### 2. `images/gemini-vpn/docker-entrypoint.sh` (The Watchdog):
- **Mechanism (ADR-0059):** Since the sidecar will share the parent's PID namespace, it will see the parent's entrypoint as PID 1.
- **The Watchdog Loop:** 
    - Implement a simple background loop: `while [ -d /proc/1 ]; do sleep 5; done`.
    - Once PID 1 is gone, the watchdog MUST terminate the sidecar process (e.g., `pkill tailscaled`).
- **Standardized Logging:** All logs MUST start with `>> [VPN]` and be redirected to `stderr`.

### 3. `docker-bake.hcl` Integration:
- Register the new `gemini-vpn` target.
- Set it to be built by default during a full rebuild.

## ✅ Validation
- **Test:** Run a mock parent container: `docker run --rm -d --name parent busybox sleep 100`.
- **Test:** Launch the sidecar: `docker run --rm -d --name sidecar --pid container:parent gemini-vpn`.
- **Action:** Stop the parent: `docker stop parent`.
- **Verify:** The sidecar container should exit automatically within 10 seconds.
