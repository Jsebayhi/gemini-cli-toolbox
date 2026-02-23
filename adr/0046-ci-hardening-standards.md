# ADR-0046: CI Hardening Standards

## Status
Proposed

## Context
The current CI pipeline is monolithic, making it difficult to debug individual failures or retry specific segments (e.g., linting vs. tests). Additionally, the signing process relies on mutable tags, which are susceptible to "tag stealing" attacks. Testing also suffers from "root leakage," where mounting the entire project root can mask missing dependencies within the container images.

## Decision
We will implement the following hardening standards:

1.  **Discrete GHA Jobs:** Break the CI into `lint`, `build-cache`, `test-bash`, `test-hub`, `scan`, and `publish`.
2.  **Bake-in-Job Strategy:** Re-run `bake` in each job using `type=gha` cache to ensure environment fidelity.
3.  **Digest-Based Signing:** Capture the image SHA256 digest from BuildKit/Docker Hub and sign the digest using Cosign.
4.  **Test Fidelity:** Mount only the specific directories required for tests (`bin`, `images`, `tests/bash`) instead of the project root.
5.  **Strict Security Scanning:** Remove `--ignore-unfixed` from Trivy scans to ensure all critical vulnerabilities are audited.

## Alternatives Considered
### 1. Monolithic Job with Parallel Shell Commands
**Why Rejected:** Poor observability and no retry logic for specific sub-tasks. Failure of one test suite requires re-running the entire build and all tests.

### 2. Tag-Based Signing
**Why Rejected:** Mutable tags can be overwritten after signing, leading to a signed "latest" tag pointing to unverified code.

## Consequences
-   Significantly improved CI reliability and debuggability.
-   Enhanced security posture through immutable signing.
-   Stronger verification of image-internal dependencies.
