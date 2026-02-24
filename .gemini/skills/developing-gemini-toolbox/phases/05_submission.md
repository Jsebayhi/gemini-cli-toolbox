# Phase 5: Submission

**Goal:** Merge the changes cleanly.

## 1. Push
```bash
git push origin <branch>
```

## 2. Pull Request (Squash-Ready)
Create the PR using a title and body that follow the project's commit message standards. Because the repository squashes PRs, the PR title and body **will become** the final commit message in the main branch.

**Note:** You MUST use the GitHub CLI (`gh`) for this. Do not use the web UI or other tools.

### Standards & Formatting
*   **Source of Truth:** Follow the [Commit & PR Content Standards](../references/commit_standards.md).
*   **Mandate:** No filler language. Detail the technical "Why". Wrap at 72 chars.

### Command Execution
Use the following template for the PR creation:

```bash
gh pr create --title "type(scope): <description>" --body "<Technical Rationale (The 'Why'). Linking the issue.>"
```
