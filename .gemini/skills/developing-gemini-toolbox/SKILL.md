---
name: developing-gemini-toolbox
description: Develops and maintains the Gemini CLI Toolbox, including Gemini Hub and Gemini CLI. Enforces strict workflows for diagnosis, architectural design, and testing. Use when modifying the codebase, fixing bugs, or adding features.
---

# Gemini CLI Toolbox Developer Guide

You are the maintainer. You MUST strictly follow this progressive workflow. Do not skip phases or take shortcuts.

## 🚦 Strict Workflow Mandate
1.  **Announcement:** At the start of every task or major step, you MUST explicitly state which Phase you are currently in (e.g., "Current Phase: 1. Alignment").
2.  **Sequential Progress:** You MUST complete each phase in order. Do not move to Architecture without Alignment, or Implementation without an approved ADR.
3.  **Verification:** You MUST run the mandatory commands in Phase 4 before proceeding to Phase 5.

## 🧠 Mental Checklist
- [ ] **Alignment:** Is the Goal/Problem clearly defined in the Issue?
- [ ] **Architecture:** Are at least 3 alternatives analyzed, documented in the ADR, and reasons for rejection clearly defined?
- [ ] **Implementation:** Are docs and code updated?
- [ ] **Validation:** Did `make local-ci` pass?
- [ ] **Submission:** Is the PR title commit-style?

## 🚀 The Workflow

### 1. Alignment (Problem Space)
**Define the Goal.** Validate the "What" and "Why".
👉 [Read Phase 1 Guide](phases/01_alignment.md)

### 2. Architecture (Solution Space)
**Design the Solution.** Explore 3 alternatives.
👉 [Read Phase 2 Guide](phases/02_architecture.md)

### 3. Implementation
Branching, coding standards, and documentation mandates.
👉 [Read Phase 3 Guide](phases/03_implementation.md)

### 4. Validation
Mandatory CI and security checks.
👉 [Read Phase 4 Guide](phases/04_validation.md)

### 5. Submission
Pushing and PR conventions.
👉 [Read Phase 5 Guide](phases/05_submission.md)

## 🛠️ Cheat Sheet
| Task | Command |
| :--- | :--- |
| **Issues** | `gh issue list` / `gh issue view` / `gh issue create` |
| **Comment** | `gh issue comment <id> --body "..."` |
| **PR** | `gh pr create --title "..." --body "..."` |
| **Test** | `make local-ci` |
| **Build** | `make build` |
| **Scan** | `make scan` |

## 📚 References
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
