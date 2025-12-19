# ADR 0002: Permission Handling Strategy (gosu)

## Status
Accepted

## Date
2025-12-17

## Context
Docker containers run as `root` by default. However, we are mounting the user's local project directory and configuration files. If the container runs as `root`, any files created by the Agent (logs, code, config) will be owned by `root` on the host system, creating a permission nightmare for the user.

## Decision
We implemented a **Dynamic Entrypoint** pattern using **`gosu`**.

1.  The container starts as `root`.
2.  The entrypoint script accepts `DEFAULT_UID` and `DEFAULT_GID` env vars (passed from the host).
3.  The script creates a user inside the container with these exact IDs.
4.  The script fixes ownership of the container's `/home` directory.
5.  The script executes the application using `exec gosu user:group`.

## Alternatives Considered
*   **`docker run --user $(id -u)`:**
    *   *Failure Mode:* The container starts as a non-root user immediately. This user lacks permissions to modify `/home` or install dependencies at runtime, causing the application to crash or freeze.
*   **`su -c ...`:**
    *   *Failure Mode:* `su` runs the command as a child process and often breaks signal forwarding (Ctrl+C) and TTY connections, causing the CLI to freeze.

## Consequences
*   **Security:** The application runs as a standard user, not root.
*   **Usability:** Host files remain owned by the host user.
*   **Complexity:** Requires a custom `docker-entrypoint.sh` script.
