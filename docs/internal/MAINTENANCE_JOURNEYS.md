# 🛠️ Internal Maintenance Journeys (QA Matrix)

The goal of this document is to track all supported user paths and variants. Maintainers must ensure these paths remain functional when updating the CLI, Hub, or Docker images.

---

## 🔑 1. Multi-Account / Multi-Profile
*   [ ] Launch `gemini-toolbox` with Google Work account on Project A.
*   [ ] Launch `gemini-toolbox` with Google Personal account on Project B.
*   [ ] Verify histories are isolated between profiles.

## 💻 2. Local Desktop
*   [ ] **Gemini Mode:** `gemini-toolbox` (Verify interactive shell).
*   [ ] **Bash Mode:** `gemini-toolbox --bash` (Verify raw shell).
*   [ ] **VS Code Integration:** Launch from VS Code terminal (Verify connection to extension).
*   [ ] **Strict Sandbox:** `gemini-toolbox --no-docker --no-ide`.

## 📱 3. Remote Access (VPN)
*   [ ] **Desktop-to-Remote:** Start with `--remote` on desktop, connect via phone Hub.
*   [ ] **Remote-to-Desktop:** Start on desktop, switch to phone, switch back to desktop (`connect` command).
*   [ ] **Remote-only:** Open Hub from phone, launch a new session, interact purely from phone.

## 🤖 4. Autonomous Bots
*   [ ] **One-shot:** `gemini-toolbox "the task"`.
*   [ ] **Hub Bot (Non-interactive):** Launch via Hub UI with task, verify auto-exit.
*   [ ] **Hub Bot (Interactive):** Launch via Hub UI with task + interactive toggle, verify session stays open.

## 🧰 5. Hub Operations
*   [ ] **Smart Restart:** Launch session in a new folder, Hub should prompt to restart and mount.
*   [ ] **Hybrid Mode:** Access Hub from same desktop, verify "VPN" fallback badge and primary localhost link.
*   [ ] **Standalone Hub:** Run `gemini-hub` manually with custom `--workspace` and `--config-root`.

## 🐚 6. Advanced Shell
*   [ ] **Debug Sandbox:** Inspect container contents using `--bash`.
*   [ ] **Persistent History:** Mount `.bash_history` and verify persistence across restarts.
