# ADR 0047: Hub Non-Root Execution and Git Identity Alignment

## Status
Proposed

## Date
2026-02-23

## Context
Initially, the `gemini-hub` component ran its Flask application as `root`. While this simplified initial setup, it created two significant issues:
1.  **Git Identity Mismatch:** Host-mounted repositories are owned by the host user (typically UID 1000). When the Hub ran as `root`, Git's "dubious ownership" security check prevented the Hub from performing introspection (e.g., checking worktree states for pruning or resolving branches for session launches).
2.  **Security Posture:** Running a network-exposed web application as `root` is a security anti-pattern.

Additionally, `gemini-toolbox` attempted to create host-path cache directories (like `.m2`) regardless of where it was running. Inside the Hub container, this led to "Permission Denied" errors because the Hub's non-root user (aligned with the host) lacked write access to the container's root-owned `/home` directory.

## Decision
We will align the Hub's security and permission model with the CLI (as defined in [ADR-0003](0003-permission-handling-gosu.md)).

1.  **Non-Root Hub:** Install `gosu` in the Hub image and update its entrypoint to dynamically create a user matching the host UID/GID and drop privileges before starting the Flask app.
2.  **Shared Socket:** Configure Tailscale to use a custom socket path (`/tmp/tailscaled.sock`) and fix its ownership at runtime to allow the non-root Hub user to query VPN status.
3.  **Guarded CLI Logic:** Update `gemini-toolbox` to skip host-directory initialization (`mkdir`) when running inside a container (detected via `/.dockerenv`), while preserving volume mounts for host-side resolution (DooD).

## Detailed Rationale

### Resolving the Worktree "Dubious Ownership"
By ensuring the Hub process runs with the same UID as the owner of the mounted Git repositories, we satisfy Git's security requirements. This allows the Hub to reliably distinguish between branch-based and headless worktrees, resolving the limitation noted in [ADR-0029](0029-worktree-retention-orphan-policy.md).

### Docker-out-of-Docker (DooD) Compatibility
In our DooD setup, `gemini-toolbox` (inside the Hub) defines session volumes using host paths. The Host Docker daemon resolves these paths. By guarding the `mkdir` logic, we prevent the Hub from trying to create these paths in its own ephemeral filesystem, while ensuring the session container still receives the correct mount instructions.

## Consequences
- **Positive:** Hub can now perform full Git introspection on host-mounted projects.
- **Positive:** Improved security by running the Hub as a non-root user.
- **Positive:** Cleaner Hub filesystem by avoiding useless host-cache directory creation.
- **Negative:** Increased complexity in the Hub entrypoint (UID/GID handling).
