# Phase 2: Implementation

**Goal:** Execute the plan with strict adherence to project standards.

## 1. Preparation
*   **Check Branch:** Ensure you are on the feature branch created in Phase 2.
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
*   **Living ADR:** Update the `adr/NNNN-name.md` file throughout implementation to reflect reality. The final state must match the code.
