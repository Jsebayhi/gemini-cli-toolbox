# Phase 1: Alignment & Exploration

**Goal:** Prevent premature implementation and ensure architectural quality.
**Output:** A clear GitHub Issue contract and a drafted ADR.

## 1. Alignment (The Firewall)
**Rule:** Do not be a "Yes Man". Clarify before acting.

1.  **Define the Goal:**
    *   **What** are we building? **Why** is it valuable?
    *   **Ambiguity Check:**
        *   **Low:** State assumptions explicitly.
        *   **High:** Ask targeted questions. Wait for user validation.
2.  **Contract:** Document the agreed Problem Statement and Goal in a GitHub Issue (`gh issue create`) **before** thinking about architecture.

## 2. Exploration (Idea Space)
**Rule:** Diverge before converging.

1.  **Brainstorming:**
    *   Propose **3 distinct architectural alternatives** (e.g., "Naive/Simple", "Robust/Scalable", "Novel/Hack").
    *   **Red-Teaming:** Challenge your own assumptions. Ask: "What if this assumption fails?"
2.  **Trade-off Analysis:**
    *   List Pros/Cons for each option.
    *   Evaluate cost vs. benefit.

## 3. Synthesis (Decision)
1.  **Select:** Choose the best solution.
2.  **Draft ADR:** Post a summary of the decision to the GitHub Issue.
    *   See `references/conventions.md` for the ADR template.
3.  **Approval:** Explicitly ask the user: *"Does this direction feel solid?"*. Wait for confirmation.
