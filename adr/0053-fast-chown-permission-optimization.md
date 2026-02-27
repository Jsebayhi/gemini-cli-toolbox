# ADR-0053: Fast-Chown Permission Optimization

## Status
Superseded by [ADR-0054](0054-fail-fast-permission-strategy.md)

## Date
2026-02-26

## Context
The Gemini CLI container (ADR-0003) uses a dynamic entrypoint to match the container user's UID/GID with the host user. To ensure the user has write access to their persistent home directory, the entrypoint previously performed an unconditional recursive ownership change (`chown -R $TARGET_UID:$TARGET_GID $HOME`) on every startup.

As the toolbox is increasingly used for large projects (e.g., those with massive `node_modules` folders or large build caches), this operation has become a significant bottleneck. Users have reported severe "input lag" or "hanging" during the container's startup phase, sometimes taking several minutes to complete the `chown -R` traversal on large volumes.

## Decision
We will implement a **Fast-Chown Optimization** in the `gemini-cli` entrypoint.

Instead of unconditionally recursing, the entrypoint will now:
1.  Verify if the home directory's **root** ownership matches the target UID/GID using `stat`.
2.  Perform the recursive `chown -R` **only** if the root ownership does not match.

## Alternatives Analyzed

### 1. Status Quo (Unconditional `chown -R`)
*   **Description:** Always run `chown -R` on startup.
*   **Pros:** Guaranteed permission consistency for all files.
*   **Cons:** Extremely slow on large volumes; unacceptable startup latency.
*   **Status:** Rejected (Reason: Performance bottleneck).

### 2. Find-based Selective Chown
*   **Description:** Use `find $HOME \! -user $TARGET_UID -o \! -group $TARGET_GID -exec chown ... {} +`.
*   **Pros:** Only modifies files with incorrect ownership.
*   **Cons:** Still requires a full directory traversal to `stat` every file. On large or networked filesystems, the traversal itself is the primary source of latency.
*   **Status:** Rejected (Reason: Does not solve the traversal latency).

### 3. Fast-Chown (Root Check)
*   **Description:** Check the root of the volume/home dir. If it matches, assume the rest is correct.
*   **Pros:** Instantaneous startup in the 99% case (re-using an existing volume). Fixes the "hang" completely for established workspaces.
*   **Cons:** Does not automatically fix files that were manually modified or created as root *inside* a correctly-owned sub-directory.
*   **Status:** Selected (Reason: Industry standard for balancing speed and safety in Docker entrypoints).

## Consequences
*   **Positive:** Near-instant container startup for existing projects, regardless of directory size.
*   **Negative:** If a user manually creates a file as `root` in a sub-directory, they may encounter "Permission Denied" and will need to manually `chown` it or temporarily change the root ownership to trigger a re-fix.
*   **Usability:** Added a `log_info` message when the fix is being applied to provide feedback during the (rare) slow path.
