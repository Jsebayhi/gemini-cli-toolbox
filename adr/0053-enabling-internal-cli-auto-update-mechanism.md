# ADR-0053: Enabling Internal CLI Auto-Update via User-Space Installation

Date: 2026-02-25

## Status

Accepted (Supersedes previous "Global Chmod" strategy)

## Context

The `@google/gemini-cli` tool includes an internal mechanism to apply updates automatically. 
In our containerized environment, the CLI was previously installed as `root` in `/usr/local/lib/node_modules`, causing runtime updates to fail for the non-root `gemini` user.

We initially considered granting global write access (`777`) to system directories, but this is non-standard and difficult to maintain across Docker layers.

## Decision

We will adopt the "User-Space Prefix" pattern for Node.js. Instead of installing the CLI into system directories, we will install it into a directory owned by the `gemini` user.

**Implementation Details:**
1.  Set `NPM_CONFIG_PREFIX` to `/home/gemini/.npm-global`.
2.  Add `/home/gemini/.npm-global/bin` to the system `PATH`.
3.  Ensure the directory is created and writable by the `gemini` user during the build.
4.  Perform the initial `npm install` using this prefix.

## Consequences

### Positive
*   **Security:** Avoids changing permissions on `/usr/local`.
*   **Reliability:** The internal auto-update mechanism works exactly as intended in a standard non-root environment.
*   **Best Practice:** Follows the recommended Node.js pattern for avoiding `sudo` with global packages.

### Negative
*   **Image Structure:** Moves the application binary from a system path to a user path, which is a minor departure from standard Linux FHS but common in Node.js environments.
