# 1. Monorepo Toolbox Structure

Date: 2025-12-19

## Status

Accepted

## Context

The project initially contained a single tool (`gemini-cli`) with all build artifacts (`Dockerfile`, `entrypoint`, `Makefile`) located in the root directory.

As the project evolved, we identified the need for:
1.  **Shared Dependencies:** A common base image (`gemini-base`) to speed up builds and manage OS updates centrally.
2.  **Scalability:** The potential to add other related CLI tools (e.g., `claude-cli`, `chatgpt-cli`) without cluttering the root.
3.  **Isolation:** Ensuring that the documentation, specs, and history of one tool do not mix with others.

## Decision

We decided to refactor the repository into a **Monorepo / Toolbox** structure:

1.  **`images/<tool-name>/`:** Every Dockerized tool resides in its own dedicated directory. This directory is self-contained, holding its own:
    *   `Dockerfile`
    *   `Makefile` (Component-level build)
    *   `README.md` (Component documentation)
    *   `adr/` (Component-specific decisions)
    *   `TECHNICAL_SPEC.md` & `ENGINEERING_LOG.md`
2.  **`bin/`:** Contains the user-facing wrapper scripts for all tools.
3.  **Root `Makefile`:** Acts as an **Orchestrator**, managing the dependency graph (e.g., "Build `gemini-base` before `gemini-cli`") and providing a unified `make build` interface.
4.  **Root `README.md` & `GEMINI.md`:** Serve as a catalog and high-level operational guide.

## Consequences

### Positive
*   **Modularity:** Each tool can be versioned, built, and documented independently.
*   **Cleanliness:** The root directory remains clean, serving only as an entry point.
*   **Extensibility:** Adding a new tool is as simple as creating a new folder in `images/`, without impacting existing tools.

### Negative
*   **Indirection:** Developers must navigate into subfolders to find specific implementation details.
*   **Build Complexity:** The root `Makefile` must explicitly manage build order and recursive make calls.
