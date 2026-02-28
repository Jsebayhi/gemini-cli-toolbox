---
name: developing-gemini-toolbox
description: Develops and maintains the Gemini CLI Toolbox, including Gemini Hub and Gemini CLI. Enforces strict workflows for diagnosis, architectural design, and testing. Use when modifying the codebase, fixing bugs, or adding features.
---

# Gemini CLI Toolbox Developer Guide

You are the maintainer. You MUST strictly follow the **Research -> Strategy -> Execution** lifecycle. Do not skip phases or take shortcuts.

## 🚦 Strict Workflow Mandate
1.  **Announcement:** At the start of every task or major step, you MUST explicitly state which Phase you are currently in (e.g., "Current Phase: 1. Alignment").
2.  **Sequential Progress:** You MUST complete each phase in order. Do not move to Architecture without Alignment, or Implementation without an approved ADR.
3.  **Verification:** You MUST run the mandatory commands in Phase 4 before proceeding to Phase 5.
4.  **Documentation:** You MUST update `GEMINI.md` (root or component) when making architectural changes or discovering new project-specific behaviors.

## 📝 Commit & PR Mandates
Because PRs are squashed, your PR title and body BECOME the final repository history. You MUST ensure they provide a high-signal technical rationale.
- **Standards:** Follow the detailed [Commit & PR Content Standards](references/commit_standards.md).
- **Rule:** Never use filler (e.g., "This PR..."). Start with the Technical "Why".
- **History:** NEVER amend a commit (`git commit --amend`). Keep the full modification history to provide a clear audit trail for the reviewer.

## 🧠 Mental Checklist
- [ ] **Alignment:** Is the Goal/Problem clearly defined through Research?
- [ ] **Architecture:** Are at least 3 alternatives analyzed, documented in the ADR, and reasons for rejection clearly defined?
- [ ] **Implementation:** Are docs and code updated?
- [ ] **Validation:** Did `make local-ci` pass?
- [ ] **Submission:** Is the PR body formatted for a squash commit (Why + Issue)?

## 🚀 The Workflow

### 1. Alignment (Problem Space / Research)
👉 [Read Phase 1 Guide](phases/01_alignment.md)

### 2. Architecture (Solution Space / Strategy)
👉 [Read Phase 2 Guide](phases/02_architecture.md)

### 3. Implementation (Execution)
👉 [Read Phase 3 Guide](phases/03_implementation.md)

### 4. Validation (Verification & Cleanup)
👉 [Read Phase 4 Guide](phases/04_validation.md)
*   **Mandate:** When working on UI features, the most valuable E2E test is the one testing the UI.
*   **Cleanup:** You MUST perform a cleanup step to identify and remove unneeded changes and simplify your code.

### 5. Submission (Delivery)
👉 [Read Phase 5 Guide](phases/05_submission.md)
*   **Action:** You MUST open the PR immediately once you have finished and verified your work.

## 🛠️ Cheat Sheet
| Task | Command |
| :--- | :--- |
| **Issues** | `gh issue list` / `gh issue view` / `gh issue create` |
| **Comment** | `gh issue comment <id> --body "..."` |
| **PR** | `gh pr create --title "..." --body "..."` |
| **Test** | `make local-ci` |
| **Build** | `make build` |
| **Scan** | `make scan` |
| **Doc** | `cat GEMINI.md` (Check for updates) |

## 📚 References
*   [Commit & PR Standards](references/commit_standards.md)
*   [ADR Best Practices](references/adr_best_practices.md)
*   [Core Mandates](references/mandates.md)
*   [DevSecOps Governance](references/devsecops.md)
*   [Architecture](docs/ARCHITECTURE_AND_FEATURES.md)
*   [Conventions](references/conventions.md)
*   [Bash Best Practices](references/bash_best_practices.md)
*   [Bash Testing](references/bash_testing.md)
*   [Python Engineering Standards](references/python_best_practices.md)
*   [General Testing](references/general_testing.md)
*   [General UI Testing](references/general_ui_testing.md)
*   [Python Testing Implementation](references/python_testing.md)
*   [Python UI Testing Implementation](references/python_ui_testing.md)
