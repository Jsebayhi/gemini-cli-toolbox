# Phase 1: Alignment (Problem Space / Research)

**Goal:** Ensure we are solving the right problem through rigorous Research.
**Output:** A clear GitHub Issue defining the **Problem** and **Goal**.

## 1. The Firewall & Research Mandate
**Rule:** Do not be a "Yes Man". Clarify before acting.
**Research:** Map the codebase, validate all assumptions, and (for bugs) reproduce the failure state before proposing a fix.
👉 **See [Core Mandates](../references/mandates.md)** for the strict Ambiguity Handling Protocol.

## 2. Problem Exploration
Explore the "Idea Space" of the *problem* itself. Use `gh issue view <number>` to read the full context and previous discussions.
*   **What** are we trying to achieve?
*   **Why** is this valuable?
*   **Is it a good idea?** Challenge the premise.
*   **Ambiguity Check:** Apply the protocol from `references/mandates.md`.

## 3. Contract (The Output)
1.  **Synthesize:** Summarize the Problem Statement and Success Criteria.
2.  **Document:** 
    *   **If an issue exists:** Post this synthesis **as a comment** on the GitHub Issue using `gh issue comment <number> --body "..."`.
    *   **If NO issue exists:** Create a new issue using `gh issue create --title "<Brief Description>" --body "<Detailed Synthesis>"`. Use the returned issue number for all subsequent steps.
3.  **Handoff:** Follow the [Session Mode Protocol](../references/mandates.md# session-mode-protocols).
    *   **Interactive:** Wait for explicit approval.
    *   **Autonomous:** Proceed to Architecture immediately after documenting.
