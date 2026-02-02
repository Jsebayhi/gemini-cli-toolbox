# Contributing Guide

## Workflow & Issue Management

This project uses a "Hybrid Agent" workflow designed for speed and clarity.

### 1. The Inbox (GitHub Issues)
*   **Role:** The single source of truth for **What** to build.
*   **Action:** All tasks must start as a GitHub Issue.
*   **Agent Rule:** Always check `gh issue list` before asking "what should I do?".

### 2. The Spec (In the Issue)
*   **Role:** The source of truth for **How** to build it.
*   **Rule:** Do **NOT** create separate spec files or "Draft ADRs" in the repo.
*   **Method:** Write the architectural plan, requirements, and constraints directly in the **Issue Description**.
    *   *Why:* This makes the Spec immediately available to the Agent via `gh issue view` without needing git branching or PRs.

### 3. Execution (The Workbench)
*   **Action:** When working on an issue:
    1.  Create a branch `issue-{id}-{short-desc}`.
    2.  Implement the code.
    3.  **Finalize the ADR:** If the feature involved a significant architectural decision, create the formal `adr/XXXX-title.md` file **as part of your implementation PR**. This promotes the "Proposed" spec from the Issue into a "Accepted" record in the codebase.

### 4. Code Style & Standards
*   **Python:** Follow `images/gemini-hub/docs/ENGINEERING_STANDARDS.md`.
*   **Bash:** Use `shellcheck`.
*   **Testing:** New features must include tests (or manual verification steps documented in the PR).
*   **CLI Updates:** If you add or modify CLI flags/arguments, you **MUST** update the corresponding bash completion script in `completions/`.

### 5. Task Sizing
Every issue **MUST** have a complexity label. If unsure, estimate.
*   `small-task`: Simple script changes, text updates, or minor UI tweaks (< 1 hour).
*   `medium-task`: Logic changes, new API endpoints, or single-component features (1-4 hours).
*   `large-task`: Major architectural changes, multi-component integration, or complex new subsystems (> 4 hours).
