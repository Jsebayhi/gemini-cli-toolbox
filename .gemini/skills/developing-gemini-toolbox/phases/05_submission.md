# Phase 5: Submission

**Goal:** Merge the changes cleanly.

## 1. Push
```bash
git push origin <branch>
```

## 2. Pull Request (Squash-Ready)
Create the PR using a title and body that follow commit message best practices. Because the repository squashes PRs, the PR title and body **will become** the final commit message in the main branch.

**Note:** You MUST use the GitHub CLI (`gh`) for this. Do not use the web UI or other tools.

### PR Title
*   **Format:** `type(scope): description` (Conventional Commits).
*   **Example:** `feat(hub): add auto-prune service`

### PR Body
The body must be a high-signal technical description.
*   **WHY:** Detail *why* the change was made, focusing on technical rationale, architectural alignment, or bug root causes.
*   **ISSUE:** Link the relevant issue (e.g., `Closes #123` or `Refs #456`).
*   **NO FILLER:** Never use phrases like "This PR...", "I updated...", or "Here are the changes...". Start directly with the technical justification.
*   **FORMAT:** Wrap lines at 72 characters. Use Markdown for lists or code blocks if they help clarify the "Why".

```bash
gh pr create --title "feat/fix: <description>" --body "<Detailed technical rationale (The 'Why'). Linking the issue.>"
```
