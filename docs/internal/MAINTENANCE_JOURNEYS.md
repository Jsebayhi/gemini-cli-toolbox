# 🛠️ Internal Maintenance Journeys (QA Matrix)

This document tracks the full end-to-end user journeys for regression testing. Unlike unit tests, these verify the cohesion between the CLI, the Hub, and the Docker container across time and devices.

---

## 🔁 Journey 1: Cross-Device Continuity
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

## 🎭 Journey 2: Profiles & Isolation
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

## 🤖 Journey 3: Bots & Hub Integration
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

## 🛡️ Journey 4: Sandboxing & Security
**Goal:** Verify security constraints.

1.  **Launch Restricted:**
    *   Run `gemini-toolbox --no-docker --no-ide`.
2.  **Attempt Breakout:**
    *   Run `docker ps`.
    *   **Verify:** Command fails (socket missing).
    *   Run `env`.
    *   **Verify:** No `GEMINI_CLI_IDE_*` variables present.

## 🔄 Journey 5: Hub Dynamic Config
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

## 🐚 Journey 6: Bash & Scripting
**Goal:** Verify non-interactive plumbing and scripting capabilities.

1.  **Bash One-Liner:**
    *   Run `gemini-toolbox --bash -c "echo 'Inside Docker' && ls -la"`.
    *   **Verify:** Output shows container file list and exits immediately.
2.  **Piping Content:**
    *   Run `echo "System Error 500" | gemini-toolbox "Explain this error"`.
    *   **Verify:** Agent receives the piped input and responds contextually.

## 🏚️ Journey 7: Legacy Config Compatibility
**Goal:** Verify backward compatibility with the simple `--config` flag.

1.  **Launch Legacy:**
    *   Run `gemini-toolbox --config /tmp/legacy-conf`.
    *   **Verify:** State files (history, cookies) are created *directly* in `/tmp/legacy-conf` (no nested `.gemini` folder).
2.  **Verify Persistence:**
    *   Restart the session.
    *   **Verify:** History is restored from that directory.

## 🔌 Journey 8: Manual & Cross-Mode Connections
**Goal:** Verify manual session management and attaching.

1.  **Launch Detached Bash:**
    *   Run `gemini-toolbox --bash --detached`.
    *   Note the Session ID (`gem-project-bash-xxxx`).
2.  **Connect Manual:**
    *   Run `gemini-toolbox connect <session-id>`.
    *   **Verify:** You are dropped into the `bash` shell of the running container.
3.  **Cross-Mode Connect:**
    *   Launch a standard CLI session detached.
    *   Run `gemini-toolbox --bash connect <cli-session-id>`.
    *   **Verify:** You get a `bash` shell inside the *CLI* container (inspecting the agent's environment).

## 🧹 Journey 9: Lifecycle & Cleanup
**Goal:** Verify containers are ephemeral and cleanup commands work.

1.  **Ephemeral Check:**
    *   Run `gemini-toolbox "quick task"`.
    *   **Verify:** After output, run `docker ps -a`. The container should NOT exist (due to `--rm`).
2.  **Hub Cleanup:**
    *   Start Hub: `gemini-hub -d --key ...`.
    *   Run `gemini-toolbox stop-hub`.
    *   **Verify:** `gemini-hub-service` container is removed.

## 🆙 Journey 10: Update Mechanism
**Goal:** Verify update mechanisms.

1.  **Explicit Update:**
    *   Run `gemini-toolbox update`.
    *   **Verify:** It attempts to `docker pull` the latest image tags.
2.  **Stale Warning (Manual Sim):**
    *   (Advanced) Manually tag an old image as `latest`.
    *   Run `gemini-toolbox`.
    *   **Verify:** A warning about the image being >7 days old appears.

## 📂 Journey 11: Volume Mounts
**Goal:** Verify manual volume injection.

1.  **Mount Host File:**
    *   Create a dummy file: `touch /tmp/host-secret.txt`.
    *   Run `gemini-toolbox -v /tmp/host-secret.txt:/tmp/secret.txt --bash -c "cat /tmp/secret.txt"`.
    *   **Verify:** Output matches content of `host-secret.txt`.
2.  **Mount Profile Extra-Args:**
    *   Add `--volume /tmp/data:/data` to a profile's `extra-args`.
    *   Run with that profile.
    *   **Verify:** `/data` exists inside the container.

## 💻 Journey 12: VS Code Integration
**Goal:** Verify the container correctly connects to the host's IDE extension.

1.  **Integrated Terminal:**
    *   Open VS Code. Open Integrated Terminal.
    *   Run `gemini-toolbox`.
    *   **Verify:** The startup log should NOT show "VS Code Integration is disabled" (unless explicitly disabled).
    *   **Verify:** `env | grep TERM_PROGRAM` output includes `vscode`.
2.  **Context Check (Manual):**
    *   (Requires extension installed) Ask Gemini: "What file is currently open?".
    *   **Verify:** It correctly identifies the active editor file.

## 📝 Journey 13: Remote Editing (Vim)
**Goal:** Verify text editing capabilities in a remote web terminal.

1.  **Launch Remote Bash:**
    *   Open Hub on Mobile/Remote device.
    *   Launch a **Bash** session.
2.  **Edit File:**
    *   Run `vim test_edit.txt`.
    *   Make changes and save (`:wq`).
    *   **Verify:** `cat test_edit.txt` shows changes.
    *   **Verify:** Latency/Rendering is usable (uses `ttyd`).
