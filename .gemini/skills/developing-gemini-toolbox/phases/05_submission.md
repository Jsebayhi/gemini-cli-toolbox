# Phase 4: Submission

**Goal:** Merge the changes cleanly.

## 1. Push
```bash
git push origin <branch>
```

## 2. Pull Request (Commit-Style)
Create the PR using a title and body that follow commit message best practices. The PR will be squashed; the title and body **will become** the final commit.

*   **Format:** `type(scope): description`
*   **Body:** Detail *why* the change was made. Link the issue.

```bash
gh pr create --title "feat/fix: <description>" --body "<Detailed commit-style body>"
```
