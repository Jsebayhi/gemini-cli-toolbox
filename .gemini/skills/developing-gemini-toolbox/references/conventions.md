# Engineering Standards & Conventions

## The Golden Rule: Documentation is Code
This project strictly enforces the pattern that documentation (`README.md`, `GEMINI.md`, `ADRs`) is the source of truth.
*   **Trigger:** If you change code that affects behavior, you **MUST** update the docs in the same commit (or PR).
*   **GEMINI.md:** Each component folder has its own `GEMINI.md` capturing specific "gotchas" and workflows.

## GitHub Interaction
**Rule:** You MUST use the GitHub CLI (`gh`) for all interactions with GitHub (issues, pull requests, etc.).
*   **Discovery:** Use `gh issue list` and `gh issue view` to understand tasks.
*   **Communication:** Post comments using `gh issue comment`.
*   **Submission:** Create PRs using `gh pr create`.

## Naming Conventions
👉 **Source of Truth:** See `GEMINI.md` (Root) Section 5: Naming Strategy.

## Code Standards
👉 **Source of Truth:**
*   **Hub (Python):** See `images/gemini-hub/docs/ENGINEERING_STANDARDS.md`.
*   **CLI (Bash):** Follow `shellcheck` guidance.

## Architecture Decision Records (ADR)
*   **Location:** `adr/`
*   **Rule (Immutability):** ADRs are **immutable historical logs**. Do not modify the "Decision" or "Context" of an existing ADR to reflect a new direction.
*   **Process:**
    1.  Propose a significant architectural change.
    2.  Write a **NEW** ADR documenting the new direction.
    3.  Update the **Status** of the old ADR to "Superseded by [ADR-XXXX]".
    4.  **Preserve History:** Do NOT remove previous "Supersedes" lines from an old ADR. Maintain the full chain (e.g., "Supersedes ADR-0001" followed by "Superseded by ADR-0038") to allow tracing the architectural evolution.
    5.  Implement the change.

### ADR Template
> **Rule for Greenfield:** If creating an ADR for a NEW system or foundational pattern, focus on the **establishment** of the standard. Do not invent a "legacy" state if one did not exist in the tracked history.

```markdown
# NNNN. Title of Decision

## Status
Proposed | Accepted | Superseded by [NNNN](link)

## Context
What is the problem we are solving? What are the constraints?

## Alternatives Considered
List at least 3 alternatives explored during Phase 2 (include all significant options considered).

### [Alternative Name 1]
*   **Description:** ...
*   **Pros/Cons:** ...
*   **Status:** Rejected
*   **Reason for Rejection:** Clearly define why this was not selected.

### [Alternative Name 2]
*   **Description:** ...
*   **Pros/Cons:** ...
*   **Status:** Rejected
*   **Reason for Rejection:** Clearly define why this was not selected.

### [Alternative Name N (Selected)]
*   **Description:** ...
*   **Pros/Cons:** ...
*   **Status:** Selected
*   **Reason for Selection:** Why is this the best choice?

## Decision
What is the final decision?

## Consequences
What are the positive and negative consequences of this decision?
```
