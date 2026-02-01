# Engineering Standards & Conventions

## The Golden Rule: Documentation is Code
This project strictly enforces the pattern that documentation (`README.md`, `GEMINI.md`, `ADRs`) is the source of truth.
*   **Trigger:** If you change code that affects behavior, you **MUST** update the docs in the same commit (or PR).
*   **GEMINI.md:** Each component folder has its own `GEMINI.md` capturing specific "gotchas" and workflows.

## Naming Conventions

### Session Identification
All components rely on a strict naming scheme to identify sessions.

**Format:** `gem-{PROJECT}-{TYPE}-{ID}`

*   **Prefix:** `gem-` (Hardcoded)
*   **Project:** Sanitized folder name (lowercase, alphanumeric + hyphens).
*   **Type:** `geminicli` or `bash` (No hyphens allowed!).
*   **ID:** Unique suffix (UUID segment).

**Example:** `gem-my-app-geminicli-a1b2`

**Why?** The Hub parses this string to group sessions by project and determine their type. Breaking this schema breaks the Hub.

## Architecture Decision Records (ADR)
*   **Location:** `adr/`
*   **Format:** `NNNN-title-of-decision.md`
*   **Recent Examples:**
    *   `0023-localhost-access-hybrid-mode.md`
*   **Process:**
    1.  Propose a significant architectural change.
    2.  Write an ADR explaining the context, decision, and consequences.
    3.  Implement the change.

## Code Style

### Python (`gemini-hub`)
*   **Linter:** `ruff`
*   **Typing:** Strict type hints required for all function signatures.
*   **Structure:**
    *   `services/`: Business logic (Tailscale, Docker, FileSystem).
    *   `routes.py`: Flask route definitions (thin wrappers).

### Bash
*   **Linter:** `shellcheck`
*   **Style:**
    *   Use `[[ ]]` over `[ ]`.
    *   Always quote variables: `"$VAR"`.
    *   Use long flags for clarity: `--volume` instead of `-v` (where possible/readable).
