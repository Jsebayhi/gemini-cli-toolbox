# Engineering Standards & Conventions

## The Golden Rule: Documentation is Code
This project strictly enforces the pattern that documentation (`README.md`, `GEMINI.md`, `ADRs`) is the source of truth.
*   **Trigger:** If you change code that affects behavior, you **MUST** update the docs in the same commit (or PR).
*   **GEMINI.md:** Each component folder has its own `GEMINI.md` capturing specific "gotchas" and workflows.

## Naming Conventions
👉 **Source of Truth:** See `GEMINI.md` (Root) Section 5: Naming Strategy.

## Code Standards
👉 **Source of Truth:**
*   **Hub (Python):** See `images/gemini-hub/docs/ENGINEERING_STANDARDS.md`.
*   **CLI (Bash):** Follow `shellcheck` guidance.

## Architecture Decision Records (ADR)
*   **Location:** `adr/`
*   **Process:** Propose -> Draft -> Implement.

### ADR Template
```markdown
# NNNN. Title of Decision
...
