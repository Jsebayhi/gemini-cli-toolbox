# ADR 0003: Network Mode Host

## Status
Accepted

## Date
2025-12-17

## Context
The Gemini CLI uses an OAuth 2.0 web flow for authentication. This process involves opening a browser on the host machine and redirecting to a local web server spawned by the CLI (e.g., `http://localhost:8085`) to capture the auth token.

## Decision
We use Docker's **Host Networking** mode (`--net=host`).

## Alternatives Considered
*   **Bridge Mode (Default) + Port Mapping (`-p 8085:8085`):**
    *   *Cons:* Requires knowing exactly which port the CLI will choose. If the CLI changes ports or tries multiple ports, mapping a single one fails.
*   **Headless Auth:**
    *   *Cons:* Copy-pasting tokens is less convenient than the automated browser flow.

## Consequences
*   **Simplicity:** Authentication works "out of the box" with the host browser.
*   **Isolation:** Network isolation is reduced (the container shares the host network stack), but this is acceptable for a CLI tool running on a personal workstation.
