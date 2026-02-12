---
name: developing-gemini-toolbox
description: Develops and maintains the Gemini CLI Toolbox, including Gemini Hub and Gemini CLI. Enforces strict workflows for diagnosis, architectural design, and testing. Use when modifying the codebase, fixing bugs, or adding features.
---

# Gemini CLI Toolbox Developer Guide

You are the maintainer. Follow this progressive workflow to ensure quality.

## 🧠 Mental Checklist
- [ ] **Alignment:** Is the Goal/Problem clearly defined in the Issue?
- [ ] **Exploration:** Is the Architecture/ADR drafted?
- [ ] **Implementation:** Are docs and code updated?
- [ ] **Validation:** Did `make local-ci` pass?
- [ ] **Submission:** Is the PR title commit-style?

## 🚀 The Workflow

### 1. Alignment & Exploration
**Do not code yet.** Validate assumptions and design architecture.
👉 [Read Phase 1 Guide](phases/01_exploration.md)

### 2. Implementation
Branching, coding standards, and documentation mandates.
👉 [Read Phase 2 Guide](phases/02_implementation.md)

### 3. Validation
Mandatory CI and security checks.
👉 [Read Phase 3 Guide](phases/03_validation.md)

### 4. Submission
Pushing and PR conventions.
👉 [Read Phase 4 Guide](phases/04_submission.md)

## 🛠️ Cheat Sheet
| Task | Command |
| :--- | :--- |
| **Test** | `make local-ci` |
| **Build** | `make build` |
| **Scan** | `make scan` |

## 📚 References
*   [Architecture](references/architecture.md)
*   [Conventions](references/conventions.md)