# Core Mandates & Interaction Protocols

## 🛡️ Workflow Enforcement
**The Workflow is the Law.** All tasks must proceed through the phases defined in `SKILL.md`.
*   **No Skipping:** Never jump to implementation before the alignment and architecture phases are formally completed and documented in the GitHub Issue.
*   **Explicit State:** Always prefix your strategy or intent with the current workflow phase.
*   **Evidence-Based Transitions:** Moving from one phase to the next requires evidence (e.g., a comment on an issue, a drafted ADR, or a passing test suite).

## 🔐 Security-First & Risk Governance
**Security is Non-Negotiable.**
*   **Zero-Debt Suppressions:** Never suppress a vulnerability to simply "get it done". Every suppression must be justified and time-bound directly within `.trivyignore`.
*   **Single Source of Truth:** Document all risk acceptances and justifications exclusively in `.trivyignore`. Do not duplicate technical vulnerability details in architectural documentation.

## 📝 Documentation Integrity
**ADRs are Immutable History.**
*   **Diff Verification:** You MUST run `git diff` after every single modification to an ADR file.
*   **Zero-Loss Policy:** You are strictly forbidden from removing sections like "Title", "Status", or "Alternatives Considered" unless explicitly instructed. If a `replace` call accidentally truncates a file, you MUST immediately use `git restore` and try a more targeted replacement.
*   **Context Preservation:** When updating implementation details in an ADR, ensure the surrounding historical context (the "Why") remains intact.

## 🔍 Mandate for Clarity (Proportional to Ambiguity)
**Primary Objective:** Avoid error due to unspoken assumptions.

### Ambiguity Handling Protocol
*   **Low Ambiguity:** Explicitly state your key assumptions -> Move to Exploration.
*   **Moderate Ambiguity:** Engage in clarification first. Use focused questioning to resolve main uncertainties -> Proceed to Exploration.
*   **High Ambiguity** (or high cost of error): Explicitly state assumptions -> **Ask user to validate them** -> Move to Exploration.

### Structured Clarification Methodology
Regardless of ambiguity level, use disciplined techniques:
1.  **Focused Questioning:** Ask one clear, targeted question at a time. For complex topics, group 2–3 closely related questions into a list.
2.  **Wait and Deepen:** After each user response, reassess. Ask follow-up questions iteratively until critical uncertainties are resolved.

## 🤖 Session Mode Protocols

### 1. Interactive Mode (Human-in-the-loop)
*   **Requirement:** Mandatory wait-for-approval at Phase 1 (Alignment) and Phase 2 (Architecture).
*   **Interaction:** Use "Radical Candor". Challenge the user. Propose alternatives.

### 2. Autonomous Mode (Agentic/Task-driven)
*   **Context:** No immediate human feedback available.
*   **Requirement:** Do not block execution. 
*   **Behavior:**
    *   **Self-Alignment:** Document assumptions and goal in the Issue. Proceed immediately.
    *   **Self-Architecture:** Propose 3 alternatives internally (in your thought process). Select one. Document the choice in the ADR.
    *   **Risk Mitigation:** If ambiguity is extremely high (destructive risk), stop and request human intervention via logs/Issue.
