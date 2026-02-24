# Phase 2: Architecture (Solution Space / Strategy)

**Goal:** Formulate a grounded Strategy to solve the problem.
**Output:** A drafted ADR and shared Strategy.

## 1. Solution Exploration & Strategy Development
**Rule:** Diverge before converging on a single Strategy.

*   **Brainstorming:** Propose **3 distinct architectural alternatives** (e.g., Naive/Simple, Robust/Scalable, Novel/Hack).
*   **Red-Teaming:** Challenge your Strategy. Ask: "What if this assumption fails?"
*   **Trade-off Analysis:** List Pros/Cons for each option.

## 2. Synthesis (The Strategy)
*   Select the best solution and formulate the implementation Strategy.
*   **Create Branch:** `git checkout -b feature/...`
*   **Draft ADR:** Create `adr/NNNN-name.md` using the template in `references/conventions.md`.
    *   **Mandate:** You MUST document at least 3 alternatives considered.
    *   **Mandate:** You MUST clearly define the "Reason for Rejection" for every non-selected alternative.
*   **Communicate:** Share a concise summary of your Strategy and the ADR draft on the GitHub Issue using `gh issue comment <number> --body "..."`.

## 3. Approval
Follow the [Session Mode Protocol](../references/mandates.md# session-mode-protocols):
*   **Interactive:** Explicitly ask: *"Does this direction feel solid?"*. Wait for confirmation.
*   **Autonomous:** Document the decision in the ADR. Proceed to implementation immediately.
