# ADR-0057: Surgical Fix for Docker-Created Root-Owned Subdirectories in Home

## Status
Accepted (Supersedes Surgical Fix in [ADR-0053](0053-fail-fast-permission-strategy.md))

## Date
2026-03-02

## Context
When a user mounts a host directory into a container at a path that does not yet exist (e.g., `~/.config/gcloud` when `~/.config` is missing in the image), the Docker daemon creates the missing parent directories as `root:root`. In the Gemini CLI Toolbox, this behavior results in `/home/gemini/.config` being owned by `root`, which blocks the container user (mapped to the host user's UID) from creating new configuration files (e.g., for `gh` or `gcloud`).

ADR-0053 ("Fail-fast permission strategy") established a "Surgical Fix" that only handled the ownership of the `$HOME` directory itself. However, it did not address subdirectories created by Docker for nested volume mounts. ADR-0053 also prohibits recursive `chown -R` on the home directory to ensure performance and safety, especially when large host directories are mounted.

## Decision
We will implement a surgical, non-recursive fix in the `docker-entrypoint.sh` of the `gemini-cli` container (and the `gemini-hub` container for parity). The entrypoint will identify root-owned subdirectories within `/home/gemini` that are NOT mount points and change their ownership to the target user.

The fix uses `find "$HOME" -xdev -user root` to identify candidates:
1.  `-xdev`: Ensures that the search does not cross mount points, protecting large host-mounted volumes (like a project workspace) from being traversed.
2.  `-user root`: Only targets items that were created by Docker or the Dockerfile as root.
3.  `is_mountpoint` check: Skips directories that are actual mount points, as their ownership should be managed on the host or may be intentionally root-owned.

This new mechanism replaces the single-directory surgical fix from ADR-0053 with a more robust discovery-based fix that handles any root-owned parent directories on the home filesystem.
