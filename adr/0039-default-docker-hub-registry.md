# 0039. Default Docker Hub Registry

## Status
Accepted

## Context
The Gemini CLI Toolbox relies on pre-built Docker images hosted on Docker Hub. To provide a "zero-config" experience, the `gemini-toolbox` and `gemini-hub` scripts need a default registry path to pull images from if they are not found locally.

Currently, this default is hardcoded to `jsebayhi/gemini-cli-toolbox`, which corresponds to the official maintenance account for the project.

## Alternatives Considered

### No Default (Strict Requirement)
*   **Description:** Require the user to always provide an image name or a registry path via environment variables.
*   **Pros:** Account-agnostic; no hardcoded strings.
*   **Cons:** Breaks the "zero-config" promise; frustrating for new users who just want to run the tool.
*   **Status:** Rejected
*   **Reason for Rejection:** High friction for the primary use case.

### Config-based Default
*   **Description:** Read the default registry from a global config file (e.g., `~/.gemini/config`).
*   **Pros:** Flexible and clean.
*   **Cons:** Requires a "setup" or "init" step before the first run, or complex logic to bootstrap the config file.
*   **Status:** Proposed (for future iteration)
*   **Reason for Rejection:** Adds complexity to the initial bootstrap logic which should remain as simple as possible.

### Hardcoded Official Account (Selected)
*   **Description:** Default to the official maintenance account (`jsebayhi`) but allow it to be easily overridden via `DOCKER_HUB_USER`.
*   **Pros:** Works out of the box for 99% of users; simple implementation.
*   **Cons:** Hardcoded personal/account string in the source code.
*   **Status:** Selected
*   **Reason for Selection:** Best balance between "zero-config" and customizability. Most users will use the official images, and developers can easily override it by setting an environment variable in their shell profile.

## Decision
Keep `jsebayhi` as the default value for `DOCKER_HUB_USER` in all scripts, ensuring it remains overridable via environment variables.

## Consequences
*   **Positive:** Zero-config experience for users using official images.
*   **Negative:** Source code contains a reference to a specific Docker Hub account.
