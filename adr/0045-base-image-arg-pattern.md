# ADR-0045: Base Image ARG Pattern

## Status
Proposed

## Context
Our Dockerfiles currently use hardcoded base images or `BASE_TAG` arguments that do not fully leverage the power of Docker Bake's `contexts` feature. This makes it difficult to substitute local targets for upstream images during CI or to build images in isolation without pre-pulling base images.

## Decision
We will adopt the `ARG BASE_IMAGE` pattern in all Dockerfiles. This involves:
1.  Defining an `ARG BASE_IMAGE` with a public, functional fallback (e.g., `ARG BASE_IMAGE=python:slim`).
2.  Using `${BASE_IMAGE}` in the `FROM` instruction.
3.  Declaring all `ARG`s before the first `FROM` for global scope.

In `docker-bake.hcl`, we will map these arguments using the `contexts` or `args` features.

## Alternatives Considered
### 1. Hardcoded FROM
**Why Rejected:** Brittle. Prevents Docker Bake from substituting local targets (e.g., `base`) for public images without manual modification of the Dockerfile.

### 2. BASE_TAG only
**Why Rejected:** Only allows modifying the tag, not the repository name. Docker Bake lookup often fails if the repository name is not exactly what it expects in the `contexts` map.

## Consequences
-   Improved flexibility for local builds and CI overrides.
-   Ensures `docker build` remains functional via the default fallback.
-   Compatible with Docker Bake's `contexts` for seamless target substitution.
