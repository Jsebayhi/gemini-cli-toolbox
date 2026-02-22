# ADR-0043: Parallel CI Optimization

## Status
Superseded by [ADR-0046](0046-native-job-isolation-and-centralized-bake-tagging.md)

## Context
Initial CI run times were 10-14 minutes due to sequential job execution, redundant build-from-scratch steps (e.g., rebuilding kcov and Playwright on every run), and multiple checkout/setup overheads.

## Decision
Optimize CI to reach < 3 minutes via several architectural changes:
1.  **GHA Layer Caching:** Move from standard Docker Hub caching to GitHub Actions' `type=gha` cache with `mode=max` for BuildKit. This persists all intermediate layers across runs.
2.  **Job Parallelism:** Separate Linting from Build & Test. Run linting (ShellCheck, Ruff) on the GitHub host for maximum speed.
3.  **In-Job Parallelism:** Inside the Build & Test job, use background processes (`&`) and `wait` to execute Bash and Python tests in parallel after the test runner images are baked.
4.  **Surgical Baking:** Use `docker-bake.hcl` to build only what is needed for each stage (e.g., build tests first, then build final apps).

## Consequences
1.  **Cycle Time:** Developers receive feedback in ~2.5 minutes instead of ~12 minutes.
2.  **Infrastructure Efficiency:** Reduced runner time saves cost and environment resources.
3.  **UX:** Log grouping (`::group::`) and parallelized security scans provide a much cleaner CI output.
