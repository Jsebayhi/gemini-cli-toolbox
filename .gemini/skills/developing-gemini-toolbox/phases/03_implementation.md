# Phase 2: Implementation

**Goal:** Execute the plan with strict adherence to project standards.

## 1. Preparation
*   **Branching:**
    ```bash
    git checkout -b feature/<name>
    # or
    git checkout -b fix/<issue-id>
    ```
*   **Context:** Load the relevant `GEMINI.md` for the component you are touching.

## 2. Coding Standards
*   **Naming:** Strictly follow `gem-{PROJECT}-{TYPE}-{ID}` for containers/hostnames.
*   **Env Vars:** Use `GEMINI_TOOLBOX_*` or `GEMINI_HUB_*` prefixes.
*   **Logs:** Use concise, actionable log messages.

## 3. Documentation (Simultaneous)
**Rule:** You MUST update documentation in the same commit as the code.
*   `GEMINI.md` (Component context)
*   `README.md` (Public features)
*   `docs/USER_GUIDE.md` (User instructions)
*   `docs/internal/MAINTENANCE_JOURNEYS.md` (QA scenarios)

## 4. Artifacts
*   **ADR:** Commit the formal ADR file (`adr/NNNN-name.md`) if established in Phase 1.
