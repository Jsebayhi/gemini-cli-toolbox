# Phase 3: Implementation

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

## 5. Verification of Changes (Diff Hygiene)
**Rule:** You MUST verify your `git diff` before every commit.
*   **Check for Deletions:** Be extremely careful when using `replace` or `write_file` tools. Accidental replacements that delete large chunks of code are the most common source of regressions.
*   **Micro-Verification:** Run a targeted `git diff HEAD` after every significant file modification.
*   **Correction:** If you realize you've accidentally deleted content, restore it immediately as a new commit (do not amend).
