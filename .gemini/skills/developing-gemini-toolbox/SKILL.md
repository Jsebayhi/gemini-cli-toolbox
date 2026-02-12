---
name: developing-gemini-toolbox
description: Develops and maintains the Gemini CLI Toolbox, including Gemini Hub and Gemini CLI. Enforces strict workflows for diagnosis, architectural design, and testing. Use when modifying the codebase, fixing bugs, or adding features.
---

# Gemini CLI Toolbox Developer Guide

You are the maintainer. Follow this progressive workflow to ensure quality.

## 🧠 Mental Checklist
- [ ] **Alignment:** Is the Goal/Problem clearly defined in the Issue?
- [ ] **Architecture:** Are 3 alternatives analyzed and ADR drafted?
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
| **Test** | `make local-ci` |
| **Build** | `make build` |
| **Scan** | `make scan` |

## 📚 References
*   [Core Mandates](references/mandates.md)
*   [Architecture](references/architecture.md)
*   [Conventions](references/conventions.md)
