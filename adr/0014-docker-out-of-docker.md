# 9. Docker-out-of-Docker (DooD) Strategy

**Date:** 2026-01-23
**Status:** Accepted

## Context
The Gemini Agent needs the ability to orchestrate containers (e.g., "start a postgres database", "run integration tests", "build this Dockerfile"). To achieve this, the container requires access to a Docker daemon.

We evaluated three approaches:
1.  **Docker-in-Docker (DinD):** Running a nested Docker daemon inside the container.
2.  **Podman:** Running rootless containers inside the container.
3.  **Docker-out-of-Docker (DooD):** Mounting the host's socket to share the host's daemon.

## Decision
We will implement **Option 3: Docker-out-of-Docker (DooD)**.

## Rationale
*   **Host Integration:** Containers started by the agent should be visible and accessible to the developer on the host (e.g., for debugging with host tools). DinD and Podman isolate these containers, creating a "black box."
*   **Performance:** DooD incurs zero virtualization overhead. DinD requires complex storage drivers (UnionFS on UnionFS) which is slow and resource-heavy.
*   **Cache Efficiency:** DooD shares the host's image cache. The agent does not need to re-download images that the user already has.
*   **Architecture Fit:** The project already utilizes "Path Mirroring" (mounting the project directory at the exact same path inside the container as on the host). This resolves the primary downside of DooD, where volume mounts from inside the container typically fail because paths don't match the host.
*   **Packaging Strategy:** We place the Docker CLI in `gemini-base` (adding ~50MB). This transforms the agent from a "Worker" (limited to installed tools) to a "Manager" (able to orchestrate any tool via Docker) across all image flavors.
*   **Security Model & Intent:** The primary goal of the sandbox is **accidental corruption prevention**, not defense-in-depth against a malicious actor. We are protecting the host from the AI agent's potential "hallucinations" or reckless shell commands (e.g., `docker rm -f $(docker ps -aq)`) rather than a focused breakout attempt. The presence of the binary is acceptable because the security boundary is the socket mount; without the socket, the agent is structurally incapable of "accidentally" orchestrating the host.

## Consequences
1.  **Image Requirement:** The base image must include `docker-ce-cli` and `docker-compose-plugin` (but not the daemon).
2.  **Wrapper Requirement:** The `gemini-toolbox` script must:
    *   Mount `/var/run/docker.sock`.
    *   Pass the host's Docker Group ID (GID) via environment variable `HOST_DOCKER_GID`.
3.  **Runtime Requirement:** The `docker-entrypoint.sh` must dynamically create a group with `HOST_DOCKER_GID` and add the `gemini` user to it, ensuring permission to write to the socket.
4.  **Security:** The agent effectively has root access to the host via the Docker socket. This is acceptable for a personal CLI toolbox but requires documentation.

## Limitation: Volume Mounts (The "Sibling" Problem)
While "Path Mirroring" (mounting the project at the exact same path inside the container as on the host) solves the issue for project files, it **does not** solve it for system mounts.

*   **The Scenario:** The host mounts `~/.m2` to `/home/gemini/.m2` inside the agent.
*   **The Action:** The agent tries to run a sibling container: `docker run -v /home/gemini/.m2:/root/.m2 maven ...`.
*   **The Failure:** The command is sent to the **Host Daemon**. The Host Daemon looks for `/home/gemini/.m2` **on the Host Filesystem**. It likely doesn't exist (or is different from the user's actual `~/.m2`).
*   **The Result:** The sibling container gets an empty directory, not the shared cache.
*   **The Constraint:** 
    *   **Relative Paths:** `docker-compose.yml` files using relative paths (`./src:/app`) **WORK** perfectly because the working directory path is identical.
    *   **Home Paths:** Agent-launched containers **CANNOT** inherit the agent's home-directory mounts (caches) easily. They must rely on the **Docker Build Cache** or their own volume management.
5.  **Implementation:** Docker integration will be **enabled by default**. A `--no-docker` flag will be added to the `gemini-toolbox` wrapper to disable it, allowing users to opt-out for a stricter sandbox environment.

## Future Risks
*   **Image Bloat:** As we add more "core" utilities to `gemini-base`, we risk losing the "lightweight" characteristic of the standard CLI. If size becomes an issue, we may need to bifurcate into `gemini-core` (text-only) and `gemini-orchestrator`.