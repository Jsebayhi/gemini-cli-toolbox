# ADR-0055: Enabling Internal CLI Auto-Update via Mount-Proof User-Space Installation

Date: 2026-02-25

## Status

Accepted

## Context

We need the `@google/gemini-cli` to be writable by the non-root `gemini` user to support its internal auto-update mechanism. 

While a user-space prefix in `/home/gemini` works, it presents a risk: if a user mounts a host directory over `/home/gemini` (common in some advanced profile configurations), the CLI installation would be shadowed and become inaccessible.

## Decision

We will use `/opt/npm-global` as the global Node.js prefix. 

**Implementation Details:**
1.  Set `NPM_CONFIG_PREFIX` to `/opt/npm-global`.
2.  Add `/opt/npm-global/bin` to the system `PATH`.
3.  During the Docker build, create `/opt/npm-global` and grant write access to the `gemini` user (UID 1000).
4.  Perform the CLI installation into this directory.

This location is outside the user's home directory, making it resilient to home-directory volume mounts while remaining fully writable for the agent's self-updates.

## Consequences

### Positive
*   **Resilience:** The CLI remains functional even if the entire `/home/gemini` directory is replaced by a volume mount.
*   **Reliability:** The internal auto-update mechanism works without root permissions.
*   **Cleanliness:** Keeps application code separate from user data/config.

### Negative
*   **Non-Standard Path:** Uses `/opt` instead of the more traditional `/usr/local` or `~`, but this is a standard practice for isolated containerized applications.
