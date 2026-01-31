# 5. Base Image Stratification

Date: 2025-12-19

## Status

Accepted

## Context

The initial design used a single `Dockerfile` that installed the OS (Debian), system utilities (`git`, `gosu`), security updates (`apt-get upgrade`), and the application (`@google/gemini-cli`).

We encountered two main issues:
1.  **Build Performance:** Rebuilding the image to update the CLI version or tweak the entrypoint required re-running `apt-get upgrade`, which is slow and bandwidth-intensive.
2.  **Caching Granularity:** We wanted to ensure the OS layer remains stable and cached while allowing frequent iteration on the Application layer.

## Decision

We decided to stratify the build into two distinct images:

1.  **`gemini-base`:**
    *   **Scope:** Operating System (Debian Bookworm), Security Updates (`apt-get upgrade`), and System Tooling (`gosu`, `git`, `procps`).
    *   **Frequency:** Built infrequently (e.g., weekly or for security patches).
    *   **Tag:** `gemini-base:latest`.

2.  **`gemini-cli`:**
    *   **Scope:** Node.js Application (`npm install -g @google/gemini-cli`) and Runtime Configuration (Entrypoint scripts).
    *   **Frequency:** Built frequently during development.
    *   **Source:** `FROM gemini-base:latest`.

## Consequences

### Positive
*   **Faster Rebuilds:** Rebuilding `gemini-cli` takes seconds instead of minutes because the heavy OS layer is pre-built and cached.
*   **Logical Separation:** System dependencies are isolated from Application dependencies.
*   **Security:** We can force a security refresh by rebuilding just the base image without touching the app logic, or vice versa.

### Negative
*   **Complexity:** Requires two `Dockerfiles` and a coordinated build order.
*   **Orchestration:** The root `Makefile` must explicitly manage the dependency chain (`base` must be built before `cli`).
