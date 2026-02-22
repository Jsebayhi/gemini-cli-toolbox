# ADR-0045: Robust Bake Contexts for Internal Base Images

## Status
Proposed

## Context
The recent CI refactor introduced `docker-bake.hcl` and switched to using named contexts (`contexts` block in Bake) to handle dependencies between images (e.g., `gemini-cli` depending on `gemini-base`).

On the `main` branch, the CI failed with:
`ERROR: target cli: failed to solve: gemini-cli-toolbox/base:latest: failed to resolve source metadata for docker.io/gemini-cli-toolbox/base:latest: pull access denied`

This happens because `buildx bake` sometimes prepends `docker.io/` to image names containing a slash in the `FROM` line, causing a mismatch with the context replacement key defined in `docker-bake.hcl`. This is particularly problematic when the tag is `latest`.

## Decision
We will use a tag-less, slash-less internal alias for the base image context. This ensures that `buildx` correctly identifies the dependency as a local target and avoids unnecessary registry lookups.

### Implementation Pattern
1.  **Dockerfile:** Use an `ARG` for the base image name with a sensible default for manual builds.
    ```dockerfile
    ARG BASE_IMAGE=gemini-cli-toolbox/base:latest
    FROM ${BASE_IMAGE}
    ```
2.  **Docker Bake:** Map an internal alias to the target and pass it via the `ARG`.
    ```hcl
    target "cli" {
      contexts = {
        base-image = "target:base"
      }
      args = {
        BASE_IMAGE = "base-image"
      }
    }
    ```

## Consequences
- **Positive:** Robust CI builds on all branches, including `main`.
- **Positive:** No unnecessary registry metadata lookups during build.
- **Positive:** Maintains standalone `Dockerfile` usability for manual builds.
- **Neutral:** Slightly more verbose `docker-bake.hcl` configuration.
