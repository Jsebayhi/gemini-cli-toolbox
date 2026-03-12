# Step 11: Decoupling Cleanup

## Goal
Remove technical debt and finalize the 2-tier architecture.

## Files to Modify
- `images/gemini-base/Dockerfile`
- `images/gemini-cli/Dockerfile`
- `README.md`
- `GEMINI.md`

## Technical Specification
1.  **Dependency Removal:**
    - From `images/gemini-base`, remove `tailscale`, `iptables`, and `iproute2`.
    - These tools are now exclusively provided by the `gemini-vpn` sidecar.
2.  **Image Optimization:**
    - Rebuild images and verify size reduction.
3.  **Documentation Finalization:**
    - Update the main `README.md` to document the 2-tier model.
    - Reference ADR-0057, ADR-0058, and ADR-0059.

## Validation
- **Full CI:** `make local-ci`
- Verify that no containers starting from `cli` or `hub` contain the `tailscaled` binary.
