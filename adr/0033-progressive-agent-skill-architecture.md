# 0033. Progressive Agent Skill Architecture

## Context
The repository uses "Agent Skills" to guide AI maintenance. The initial implementation was fragmented, contained redundant static snapshots of system architecture (leading to documentation rot), and dumped all procedural details into the main context, causing "context compaction" and weakening agent accuracy.

## Options Considered
1.  **Monolithic SKILL.md:** Easy to search but heavy on the context window.
2.  **Fragmented references:** Reduced bloat but lacked a cohesive, enforceable workflow.
3.  **Progressive Disclosure (Chosen):** Lean high-level map linking to specific phase sub-files.

## Decision
We implemented a **5-Phase Progressive Workflow** for the `developing-gemini-toolbox` skill.

1.  **Alignment (Problem Space):** Rigorous "What/Why" definition documented in an Issue comment.
2.  **Architecture (Solution Space):** Divergent exploration (3 alternatives) and Draft ADR creation on the branch.
3.  **Implementation:** Coding with "Living ADR" updates and simultaneous doc updates.
4.  **Validation:** Mandatory local CI (`make local-ci`).
5.  **Submission:** Commit-style PR formatting.

We also moved the "Clarity/Ambiguity" mandates to a dedicated reference file to ensure high-performance interactions.

## Consequences
-   **Positive:** Significantly reduced token usage in the primary context window.
-   **Positive:** Enforced architectural quality via mandatory alternatives and ADRs.
-   **Positive:** Eliminated documentation rot by linking to repo-root sources of truth (`GEMINI.md`, `Makefile`).
-   **Negative:** Requires agents to follow links across multiple files (mitigated by clear "Read Phase Guide" pointers).
