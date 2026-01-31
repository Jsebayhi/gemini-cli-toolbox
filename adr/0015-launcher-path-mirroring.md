# 13. Hub as a Session Launcher (Write Access)

Date: 2026-01-25

## Status

Proposed

## Context

Currently, the Gemini Hub is a read-only dashboard. It displays active sessions but cannot start new ones. To start a session, the user must still have SSH/Terminal access to the host machine to run `gemini-toolbox --remote`.

We want to enable "Remote Session Creation" directly from the Hub UI (e.g., from a phone), allowing the user to browse their host's projects and launch a Gemini environment for them.

## The Challenge: Path Mapping

To launch a container, the Hub needs to tell the Docker Daemon (on the host) which **Host Directory** to mount.
*   The Hub runs inside a container.
*   Containers normally have an isolated filesystem view.
*   If the Hub sees `/workspace/project-a`, it doesn't necessarily know that this corresponds to `/home/user/projects/project-a` on the host.

## Decision

We will implement a **"Path Mirroring"** strategy combined with **Docker Socket Mounting**.

### 1. Docker Access
The Hub container will mount the host's Docker socket (`/var/run/docker.sock`).
*   **Authority:** This gives the Hub the ability to spawn sibling containers.
*   **Security:** This effectively grants root privileges to the Hub container. This is accepted given the "Personal Toolbox" nature of the project, provided we document it clearly.

### 2. Workspace Mirroring
When starting the Hub, the user must specify a **Workspace Root** (defaulting to the current directory or a configured projects folder).
*   **Mirror Mount:** We mount this host directory to the **exact same path** inside the Hub container.
    *   Host: `/home/user/projects`
    *   Container: `/home/user/projects`
*   **Benefit:** Any path the Hub sees (e.g., `/home/user/projects/my-app`) is guaranteed to be a valid path on the Host.

### 3. Launcher Logic
The Hub will provide a file browser UI restricted to the Workspace Root.
When the user selects a directory and clicks "Launch":
1.  The Hub verifies the directory exists locally.
2.  The Hub constructs a `docker run` command.
3.  **Crucially:** It uses the **absolute path** of the directory as the volume source.
    *   `-v /home/user/projects/my-app:/home/user/projects/my-app`
4.  It passes the `GEMINI_SESSION_ID` and other metadata as defined in [ADR-0012](./0012-naming-consistency.md).

## Consequences

### Positive
*   **True Remote Autonomy:** Users can start work on a project without ever touching the host console.
*   **Simplicity:** No need for a separate "Host Agent" process; Docker does all the heavy lifting.
*   **Consistency:** Working directory inside the session matches the host path, reducing confusion.

### Negative
*   **Scope Restriction:** The Hub can only launch projects that reside within the mounted Workspace Root. It cannot access arbitrary paths on the host (e.g., `/tmp` or a second drive) unless multiple roots are mounted.
*   **Privilege:** The Hub container becomes a high-value target if exposed to the public internet (mitigated by Tailscale isolation).
