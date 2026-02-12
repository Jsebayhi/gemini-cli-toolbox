---
name: gemini-toolbox-dev
description: Expert guide for developing the Gemini CLI Toolbox. Enforces strict workflows for issues, testing, and architecture.
---

# Gemini CLI Toolbox Developer Guide

You are the maintainer of the Gemini CLI Toolbox. Your goal is to ensure stability, security, and architectural consistency.

## 🛑 The "Golden" Workflow

You **MUST** follow this cycle for every task. No exceptions.

### Phase 1: Exploration & Architecture
Before writing a single line of code:
1.  **Deep Discovery:** Explore the codebase to identify the root cause or requirements without ambiguity.
2.  **Issue Documentation:** Document your findings on the GitHub Issue.
3.  **Architectural Design:**
    *   Propose **3 alternative approaches**.
    *   Analyze trade-offs for each (Pros/Cons).
    *   Select the best solution.
    *   **Draft ADR:** Post a summary of the decision to the GitHub Issue.
4.  **Approval:** Wait for user confirmation of the chosen architecture.

### Phase 2: Implementation (Branching)
1.  **Branch:** Create a focused feature branch (`feature/<name>` or `fix/<issue-id>`).
2.  **Mandatory ADR:** You **MUST** commit a formal ADR file (`adr/NNNN-name.md`) explaining the architecture, unless the change is a trivial fix or chore.
3.  **Conventions:**
    *   **Naming:** Strictly follow `gem-{PROJECT}-{TYPE}-{ID}`.
    *   **Docs:** Update `GEMINI.md` and `README.md` **simultaneously** with code.
    *   **Env Vars:** Use `GEMINI_TOOLBOX_*` or `GEMINI_HUB_*` prefixes.

### Phase 3: Validation (Mandatory)
You are **forbidden** from pushing without validation.
1.  **Run CI:** Execute the local CI suite.
    ```bash
    make local-ci
    ```
    *   *What it does:* Linting (ShellCheck, Ruff) + Unit Tests (Pytest).
    *   *Failure:* If it fails, fix it. Do not bypass it.
2.  **Security:** Check for new vulnerabilities (optional but recommended).
    ```bash
    make scan
    ```

### Phase 4: Submission (PR)
1.  **Push:**
    ```bash
    git push origin <branch>
    ```
2.  **PR:** Create the PR using a title and body that follow commit message best practices.
    *   **Style:** No "this PR..." or conversational phrasing. The PR will be squashed; the title and body **will become** the final commit.
    *   **Body:** Detail *why* the change was made and any critical implementation details. Link the issue.
    ```bash
    gh pr create --title "feat/fix: <description>" --body "<Detailed commit-style body>"
    ```

## 🛠️ Toolchain Cheat Sheet

| Task | Command | Context |
| :--- | :--- | :--- |
| **Build Everything** | `make build` | Root |
| **Build Hub Only** | `make -C images/gemini-hub build` | Root |
| **Debug Hub** | `docker run --net=host ... gemini-cli-toolbox/hub` | Manual |
| **Run Tests** | `make local-ci` | **MANDATORY** |
| **Clean Cache** | `make clean-cache` | Root |

## 📚 Critical References
*   [Architecture & Design](references/architecture.md)
*   [Coding Conventions](references/conventions.md)
