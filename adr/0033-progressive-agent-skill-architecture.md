# ADR-0033: Progressive Agent Skill Architecture

## Context
As the repository grows, "Agent Skills" are required to guide AI maintainers. To ensure these skills are effective, we must establish a design pattern that prevents context bloat, documentation rot, and premature implementation.

## Options Considered
1.  **Monolithic SKILL.md:** Simple but consumes excessive tokens in the primary context window, leading to "context compaction" and reduced agent accuracy.
2.  **Progressive Disclosure (Chosen):** A lean high-level map linking to specific phase sub-files. This optimizes token usage and enforces a step-by-step process.

## Decision
We established a **5-Phase Progressive Workflow** for the `developing-gemini-toolbox` skill.

1.  **Alignment (Problem Space):** Mandatory definition of "What/Why" documented in a GitHub Issue comment before any architectural design.
2.  **Architecture (Solution Space):** Mandatory divergent exploration (3 alternatives) and creation of a "Living ADR" file on the feature branch.
3.  **Implementation:** Focused coding with simultaneous updates to the "Living ADR" and all user-facing documentation (`GEMINI.md`, `USER_GUIDE.md`, etc.).
4.  **Validation:** Mandatory local CI execution (`make local-ci`).
5.  **Submission:** Enforced "Commit-style" formatting for Pull Requests.

The architecture relies on linking to repository sources of truth (e.g., root `GEMINI.md`, `Makefile`) instead of duplicating information within the skill.

## Consequences
-   **Positive:** Optimizes agent context window by loading details only when needed.
-   **Positive:** Enforces architectural quality through mandatory alternatives and documented problem definitions.
-   **Positive:** Prevents documentation rot by establishing a single source of truth.
-   **Negative:** Requires agents to follow links across multiple files.