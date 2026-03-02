# ADR-0057: Surgical Fix for Docker-Created Root-Owned Subdirectories in Home

## Context
When a user mounts a host directory into a container at a path that does not yet exist (e.g., `~/.config/gcloud` when `~/.config` is missing in the image), the Docker daemon creates the missing parent directories as `root:root`. In the Gemini CLI Toolbox, this behavior results in `/home/gemini/.config` being owned by `root`, which blocks the container user (mapped to the host user's UID) from creating new configuration files (e.g., for `gh` or `gcloud`).

ADR-0053 ("Fail-fast permission strategy") prohibits recursive `chown -R` on the home directory to ensure performance and safety, especially when large host directories are mounted.

## Decision
We will implement a surgical, non-recursive fix in the `docker-entrypoint.sh` of the `gemini-cli` container. The entrypoint will identify root-owned subdirectories within `/home/gemini` that are NOT mount points and change their ownership to the target user.

The fix uses `find "$HOME" -xdev -user root` to identify candidates:
1.  `-xdev`: Ensures that the search does not cross mount points, protecting large host-mounted volumes (like a project workspace) from being traversed.
2.  `-user root`: Only targets items that were created by Docker or the Dockerfile as root.
3.  `is_mountpoint` check: Skips directories that are actual mount points, as their ownership should be managed on the host or may be intentionally root-owned.

## Alternatives Considered
### Option A: Pre-create host paths in `gemini-toolbox`
The host wrapper script could attempt to pre-create the parent directories on the host. However, this is brittle as it requires parsing complex Docker mount arguments and assumes the mount point is always relative to the host's home directory.

### Option B: Recursive `chown -R` in entrypoint
Explicitly rejected by ADR-0053 due to performance impact on large volumes and potential safety risks.

### Option C: Manual User Intervention
Users could be instructed to fix permissions manually. This is a poor user experience for a "zero-config" toolbox and leads to recurring support issues.

## Consequences
- **Positive:** Tools like `gcloud` and `gh` will work out-of-the-box even if their config directories were auto-created by Docker.
- **Positive:** Performance remains high as the search is limited to the container's writable layer and excludes large mount points.
- **Neutral:** The entrypoint log will show "Fixing root-owned home sub-items" when this occurs.
- **Constraint:** This only fixes top-level and nested directories *on the same device* as `$HOME`. If a user mounts something very deep, multiple parents might need fixing, which `find` handles as long as they are on the same filesystem.
