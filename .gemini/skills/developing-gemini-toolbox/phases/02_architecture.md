# Phase 2: Architecture (Solution Space)

**Goal:** Design the optimal solution.
**Output:** A drafted ADR in the GitHub Issue.

## 1. Solution Exploration
**Rule:** Diverge before converging.

*   **Brainstorming:** Propose **3 distinct architectural alternatives** (e.g., "Naive/Simple", "Robust/Scalable", "Novel/Hack").
*   **Red-Teaming:** Challenge your own assumptions. Ask: "What if this assumption fails?"
*   **Trade-off Analysis:** List Pros/Cons for each option.

## 2. Synthesis
*   Select the best solution.
*   **Create Branch:** `git checkout -b feature/...`
*   **Draft ADR:** Create `adr/NNNN-name.md` using the template.
*   **Communicate:** Post a link to the draft ADR on the GitHub Issue for review.

## 3. Approval
Follow the [Session Mode Protocol](../references/mandates.md# session-mode-protocols):
*   **Interactive:** Explicitly ask: *"Does this direction feel solid?"*. Wait for confirmation.
*   **Autonomous:** Document the decision in the ADR. Proceed to implementation immediately.
