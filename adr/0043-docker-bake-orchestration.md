# ADR-0043: Docker Bake Orchestration

## Status
Accepted

## Context
As the repository grows to include multiple images (Base, Hub, CLI, Preview, and Test Runners), managing builds via a shell script or individual `Makefiles` has become brittle. Parallelism was difficult to coordinate, and build caching was inconsistent across environments.

## Decision
We will centralize all image build logic into a single `docker-bake.hcl` file.
1.  **Declarative Syntax:** Use HCL to define targets and their dependencies (e.g., CLI depends on Base).
2.  **Inheritance:** Use the `inherits` feature to share common cache and argument logic across all targets.
3.  **Named Contexts:** Use BuildKit's named contexts to map local directories (like `bin/`) directly into the Docker build without requiring manual `cp` steps.

## Consequences
1.  **Speed:** BuildKit can build independent targets in parallel automatically.
2.  **Consistency:** Local builds (`make build`) and CI builds use the exact same logic.
3.  **Hermeticity:** Builds are no longer dependent on the host's shell state for artifact preparation.
4.  **Simplicity:** Sub-Makefiles in image directories are removed to eliminate configuration drift.
