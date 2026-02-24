# Commit & PR Content Standards

This document is the Single Source of Truth for how we document changes in the repository history. 

## 1. Professional Rigor Mandate
Because this project uses a squash-on-merge strategy, your PR title and body BECOME the final repository history. You must treat them with the highest level of technical rigor.

## 2. PR/Commit Title (Conventional Commits)
Use the `type(scope): description` format.
- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- **Scope:** The component or module (e.g., `hub`, `cli`, `skill`, `bake`).
- **Description:** Imperative, present tense, lowercase (e.g., "add auto-prune service").

## 3. PR/Commit Body (The Technical "Why")
The body MUST detail **WHY** the change was made, focusing on technical rationale, architectural alignment, or bug root causes.

### Rules
- **No Filler:** NEVER use phrases like "This PR...", "I updated...", "Here are the changes...", or "I'm fixing...". Start directly with the technical justification.
- **Why, Not Just What:** Explain the reasoning behind the implementation, especially if it involved trade-offs or complex logic.
- **Issue Linking:** Explicitly link the relevant issue (e.g., `Closes #123` or `Refs #456`).
- **Professional Tone:** Use technical language. Focus on long-term maintainability.

### Formatting
- **Line Length:** Wrap lines at 72 characters to ensure readability in git log and terminal UIs.
- **Structure:** Use bullet points or small paragraphs to separate distinct technical reasons.

## 4. Examples

### Good (High Signal)
```markdown
Reinforce the developer workflow and improve PR quality across all agent sessions.

- Codify the Research-Strategy-Execution lifecycle in GEMINI.md and SKILL.md.
- Mandate strict Research (codebase mapping, bug reproduction) and Strategy phases.
- Enforce 'No Filler' PR bodies that focus on technical 'Why' and issue linking.

These changes ensure consistent high-signal repository history and rigorous
engineering practices for all AI agent contributors.

Refs #104
```

### Bad (Low Signal)
```markdown
I have updated the skill to make it better. I added some stuff about PRs.
I also changed the GEMINI.md file. This PR fixes the issue.
```
