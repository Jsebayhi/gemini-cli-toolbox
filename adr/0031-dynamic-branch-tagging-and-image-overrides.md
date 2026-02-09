# 31. Dynamic Branch Tagging and Image Overrides

Date: 2026-02-07

## Status

Accepted

## Context

As the project grows, multiple developers or CI jobs might work on different features simultaneously. 
Previously:
1.  **Tag Collisions:** All builds used the `latest` tag locally. If a developer switched branches and ran `make build`, the `latest` image for branch A was overwritten by branch B.
2.  **CI Fragility:** The CI security scan (Trivy) was hardcoded to check the `latest` tag. On a feature branch PR, the scan would either check a stale `latest` image or fail if the image wasn't found.
3.  **Lack of Flexibility:** There was no easy way for a user to test a custom image (e.g., a local build of a fork) using the `gemini-toolbox` or `gemini-hub` wrappers without manually retagging it as `latest`.

## Decision

We implemented a dynamic tagging strategy and explicit image overrides.

### 1. Dynamic Branch-Based Tagging
Component Makefiles now calculate an `IMAGE_TAG` based on the current Git branch:
*   **`main` branch:** Uses `latest` (Stable).
*   **Feature branches:** Uses `latest-{branch-name}` (e.g., `latest-feat-set-image`).
*   **Why:** This isolates local builds and CI environments, ensuring that branch-specific images are preserved and correctly identified.

### 2. Automated Resolution in Wrappers
The `gemini-toolbox` and `gemini-hub` scripts were updated to automatically detect the branch and resolve the image:
1.  **Branch Detection:** If inside a Git repository and not on `main`, the script constructs a branch-specific tag.
2.  **Prioritization:** It checks for the existence of the branch-specific local image.
3.  **Fallback:** If the specific image doesn't exist, it falls back to the official remote `latest` image.
4.  **Zero-Configuration:** This makes the dynamic tagging transparent to the user; they always use the "best" available image for their current context.

### 3. Explicit Image Override (`--image`)
We introduced an `--image <name>` flag to all wrapper scripts.
*   **Function:** This flag bypasses all auto-resolution logic and forces the use of the specified image.
*   **Use Case:** Development of experimental images, testing third-party forks, or pinning to a specific version.

### 4. CI/CD Integration
The CI workflow was updated to be "Tag-Aware":
*   **`print-image` target:** Component Makefiles now provide a `print-image` target that outputs the full `image:tag` string for the current branch.
*   **Dynamic Scanning:** The CI uses these targets to resolve the correct image to scan with Trivy, ensuring that PRs are always validated against the code they contain.

### 5. Isolation in Multi-Worktree Environments
To align with the project's strategy of using Git Worktrees for task isolation (see ADR-0026), we decided that image resolution must be context-aware:
*   **Contextual Branch Identification:** By utilizing `git rev-parse --is-inside-work-tree`, the toolbox identifies the branch checked out in the current working directory, regardless of whether it is the main repository or a secondary worktree.
*   **Environment Integrity:** This ensures that concurrent development tasks on different branches correctly resolve to their respective local images, preventing environment leakage and ensuring a seamless transition between isolated tasks.

## Consequences

### Positive
*   **Isolation:** Developers can maintain multiple branch-specific images locally without interference.
*   **CI Correctness:** Security scans in PRs now accurately reflect the branch's code.
*   **Flexibility:** Power users can easily point the toolbox to any image.

### Negative
*   **Disk Usage:** Multiple branch-specific images might accumulate locally (mitigated by standard `docker image prune` or explicit cleanup).
*   **Complexity:** The Makefile logic for tag calculation is slightly more complex than hardcoded strings.
