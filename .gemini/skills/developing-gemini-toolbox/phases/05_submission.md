# Phase 5: Submission

**Goal:** Merge the changes cleanly.
**Mandate:** You MUST open the PR immediately once you have finished and verified your work through the lifecycle.

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

## 3. Addressing Feedback
When a reviewer provides feedback or requests changes:
*   **Respond to EVERY Comment:** You MUST respond to each review comment individually.
*   **State Agreement/Disagreement:** 
    *   If you agree, state that you have addressed the feedback and how (e.g., "Acknowledged. I've restored the section in commit X.").
    *   If you disagree, provide a clear, technical rationale for your disagreement.
*   **Verification:** Ensure all requested changes are verified and pass all tests before asking for another review.
