# ADR-0046: Native Job Isolation and Centralized Bake Tagging

## Status
Proposed

## Context
The previous CI system (ADR-0043) used background shell processes (`&`) within a single GitHub runner to achieve speed. While fast, this led to resource contention, interleaved logs that are hard to debug, and a "tag mismatch" bug on the `main` branch (ADR-0045) because tagging logic was scattered across the Makefile, GHA YAML, and Bake.

## Decision
We will refactor the CI into a professional-grade pipeline using native GitHub Actions jobs and centralized logic.

### 1. Job Isolation
We will split the pipeline into distinct jobs:
- **Lint:** (Existing) Runs linters.
- **Build:** Bakes all images and populates the `type=gha` cache.
- **Test (Matrix):** Runs Bash and Hub tests in isolated runners.
- **Scan:** Runs security scans in an isolated runner.
- **Publish:** Handles pushing, signing, and documentation updates.

### 2. Centralized Tagging Logic (Bake Functions)
We will move all tagging logic into `docker-bake.hcl` using HCL functions. The CI and Makefile will only pass the raw `GITHUB_REF` and `GITHUB_EVENT_NAME`.
This ensures that `make build` locally and the CI runner always produce identical image names.

### 3. Strict Security Scanning
We will remove the `--ignore-unfixed` flag from Trivy. All critical vulnerabilities must be either fixed or explicitly acknowledged in `.trivyignore`.

### 4. "Bake-in-Every-Job" Strategy
Instead of passing heavy Docker images as GHA artifacts (which is slow), we will re-run `docker buildx bake` in every job. Because we use `type=gha` cache with `mode=max`, these subsequent builds will be near-instant, providing "Build Once, Test Many" semantics with high performance.

## Consequences
- **Positive:** Robust resource management (no OOMs).
- **Positive:** Clean, searchable logs in the GitHub UI.
- **Positive:** 1:1 parity between local and CI tagging.
- **Positive:** No security blind spots.
- **Negative:** Slightly more GHA boilerplate in `ci.yml`.
