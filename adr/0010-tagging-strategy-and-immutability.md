# 2. Tagging Strategy and Immutability

Date: 2026-01-22

## Status

Accepted

## Context

The Docker images in this project are tagged using the version of the underlying external tool (e.g., the `@google/gemini-cli` version) rather than an independent versioning system for the toolbox itself. 

We considered enforcing tag immutability in the Docker registry to ensure that once a versioned tag (e.g., `X.Y.Z-stable`) is pushed, it cannot be overwritten. This is a common best practice for reproducibility.

## Decision

We decided **not** to enforce tag immutability and **not** to introduce a separate versioning system for the toolbox wrapper.

The rationale is as follows:
1.  **Dependency-Driven Tagging:** Since we tag based on the Gemini CLI version, we do not control the release cadence of the version numbers.
2.  **Maintainability:** If we discover a bug in our `Dockerfile`, `docker-entrypoint.sh`, or wrapper logic, we need the ability to release a fix for the *current* Gemini CLI version. With immutable tags, we would be unable to update the image for a specific version until Google releases a new version of the CLI.
3.  **Simplicity:** The project follows a simple weekly release cycle (Friday morning builds). For the current scope, overwriting tags with improved image builds is preferred over managing complex metadata or "patch" versions (e.g., `X.Y.Z-v2-stable`).

## Consequences

### Positive
*   **Ease of Hotfixing:** We can deploy security updates or bug fixes to the container environment immediately without waiting for an upstream release.
*   **Reduced Overhead:** No need to track and increment a separate project version alongside the external tool version.

### Negative
*   **Reproducibility Risk:** A user pulling the same tag at two different points in time might get a slightly different image (though the Gemini CLI version will be identical). This is mitigated by our predictable weekly build schedule.
