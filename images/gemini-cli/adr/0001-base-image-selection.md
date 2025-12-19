# ADR 0001: Base Image Selection

## Status
Accepted

## Date
2025-12-17

## Context
The Gemini CLI functions not just as a chatbot, but as an Agent capable of executing shell commands (`ls`, `grep`, `find`) on the user's project. To ensure reliability, the container environment must provide a standard, predictable Linux toolchain. We also faced performance issues with input lag in interactive sessions.

## Decision
We chose **`node:20-bookworm-slim`** (Debian 12) as the base image.

## Alternatives Considered
*   **Alpine Linux (`node:20-alpine`):**
    *   *Pros:* Significantly smaller image size (~150MB vs ~600MB).
    *   *Cons:* Uses `musl` libc instead of `glibc`.
    *   *Failure Mode:* We observed significant input lag/latency when running interactive Node.js sessions on Alpine.
    *   *Failure Mode:* Alpine provides BusyBox versions of standard tools. If the Agent attempts to use GNU-specific flags (e.g., `grep -P`), it would fail, breaking the agent's core functionality.
*   **Ubuntu (`ubuntu:24.04`):**
    *   *Pros:* Modern, familiar.
    *   *Cons:* Slightly larger than Debian Slim; less "standard" as a container base for Node.js than Debian.

## Consequences
*   **Size:** The image is larger (~600MB) than an Alpine equivalent.
*   **Compatibility:** We guarantee 100% compatibility with standard Linux commands, ensuring the Agent can work effectively.
*   **Performance:** Input handling is smooth due to `glibc` support.
