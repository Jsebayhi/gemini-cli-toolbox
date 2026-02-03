# 🛠️ Internal Maintenance Journeys (QA Matrix)

This document tracks the full end-to-end user journeys for regression testing. Unlike unit tests, these verify the cohesion between the CLI, the Hub, and the Docker container across time and devices.

---

## 🔁 Journey 1: The Commuter (Cross-Device Continuity)
**Goal:** Verify session persistence and connectivity handoff between local and remote clients.

1.  **Start on Desktop:**
    *   Run `gemini-toolbox --remote`.
    *   Verify the CLI starts and the Hub URL is displayed.
    *   Start a long-running task (e.g., `gemini -i "List all files"`).
2.  **Switch to Mobile:**
    *   Open Hub on phone (`http://gemini-hub:8888`).
    *   Tap the session card.
    *   Verify you can see the previous output and type new commands.
3.  **Return to Desktop:**
    *   Run `gemini-toolbox connect <session-id>`.
    *   Verify you re-attach to the *same* tmux session (history preserved).

## 🎭 Journey 2: The Context Switcher (Profiles)
**Goal:** Verify isolation of state and configuration between profiles.

1.  **Profile A (Work):**
    *   Run `gemini-toolbox --profile /tmp/work`.
    *   Ask Gemini to "Remember my name is Alice".
    *   Exit.
2.  **Profile B (Personal):**
    *   Run `gemini-toolbox --profile /tmp/personal`.
    *   Ask Gemini "What is my name?".
    *   **Verify:** It does *not* know your name (Isolation confirmed).
3.  **Persistence:**
    *   Run `gemini-toolbox --profile /tmp/work` again.
    *   Ask "What is my name?".
    *   **Verify:** It remembers "Alice".

## 🤖 Journey 3: The Automation Loop (Bots & Hub)
**Goal:** Verify the autonomous agent flow from the Hub UI.

1.  **Launch Bot:**
    *   Open Hub on Desktop.
    *   Click "New Session".
    *   Enter Task: `"echo 'Hello World' > test.txt"`.
    *   Uncheck "Interactive".
    *   Click Launch.
2.  **Verify Execution:**
    *   Wait for the container to exit (status update in Hub).
    *   Check the host folder for `test.txt`.
3.  **Inspect:**
    *   Launch a **Bash** session from the Hub in the same folder.
    *   Run `cat test.txt`.
    *   **Verify:** Content is "Hello World".

## 🛡️ Journey 4: The Paranoid Auditor (Sandboxing)
**Goal:** Verify security constraints.

1.  **Launch Restricted:**
    *   Run `gemini-toolbox --no-docker --no-ide`.
2.  **Attempt Breakout:**
    *   Run `docker ps`.
    *   **Verify:** Command fails (socket missing).
    *   Run `env`.
    *   **Verify:** No `GEMINI_CLI_IDE_*` variables present.

## 🔄 Journey 5: The Hot-Swapper (Hub Dynamic Config)
**Goal:** Verify the Hub adapts to new workspaces on the fly.

1.  **Start Hub:**
    *   Run `gemini-hub` (or `gemini-toolbox --remote` in `/folderA`).
2.  **Add Scope:**
    *   Run `gemini-toolbox --remote` in `/folderB`.
    *   **Verify:** The script detects the running Hub doesn't have `/folderB` mounted.
    *   **Verify:** It prompts to "Merge and Restart".
    *   Confirm the restart.
3.  **Check Visibility:**
    *   Refresh the Hub UI.
    *   **Verify:** Both `/folderA` and `/folderB` are available in the "New Session" wizard.