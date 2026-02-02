# 🗺️ Gemini CLI Toolbox: User Journeys

This document describes standard "User Paths" or "Journeys" when using the project. It helps you understand how the different components (CLI, Hub, Docker, VPN) work together in real-world scenarios.

---

## 👩‍💻 Journey 1: The Local Power Coder
*   **Goal:** Use Gemini to refactor code inside VS Code with zero host pollution.
*   **Path:**
    1.  User opens a terminal in VS Code.
    2.  Runs `gemini-toolbox`.
    3.  The container starts, automatically detects the VS Code environment, and connects to the host's Companion Extension.
    4.  User types: `"Refactor the current file to use async/await"`.
    5.  Gemini reads the context from the IDE, generates a diff, and applies it.
    6.  User reviews and commits.
*   **Outcome:** High-productivity AI assistance with no Node.js or CLI installation required on the host.

## 📱 Journey 2: The Remote Troubleshooter
*   **Goal:** Respond to an incident or fix a bug while away from the computer.
*   **Path:**
    1.  User starts a remote session from the desktop before leaving: `gemini-toolbox --remote`.
    2.  Later, from a phone/tablet, the user opens `http://gemini-hub:8888`.
    3.  User taps the active project card.
    4.  A web terminal opens. User interacts with Gemini to diagnose the issue.
    5.  User needs to edit a config file manually: They launch a new **Bash** session from the Hub's "New Session" wizard.
    6.  They use `vim` in the browser to fix the file.
*   **Outcome:** Full desktop-class development power on any mobile device.

## 🤖 Journey 3: The Background Bot
*   **Goal:** Delegate a tedious task to an autonomous agent.
*   **Path:**
    1.  User opens the Gemini Hub.
    2.  User clicks "+ New Session" and selects a project.
    3.  In the "Initial Task" field, they type: `"Search the codebase for TODOs and create a report in docs/TODO_REPORT.md"`.
    4.  They uncheck **Interactive** and click **Launch**.
    5.  The Hub starts a detached container. Gemini executes the task in the background.
    6.  User checks the Hub logs later to confirm completion.
*   **Outcome:** Asynchronous task delegation; the user continues working on other things while the bot handles the chores.

## 🛡️ Journey 4: The Security Auditor
*   **Goal:** Analyze a suspicious third-party repository safely.
*   **Path:**
    1.  User clones the repo into a temporary folder.
    2.  User runs `gemini-toolbox --no-docker --no-ide`.
    3.  This ensures the agent is strictly trapped in the container with no access to the host's Docker socket or IDE.
    4.  User asks: `"Analyze this shell script for any malicious network calls"`.
*   **Outcome:** Secure, isolated analysis of untrusted code.

## 🧪 Journey 5: The Experimenter (Sandboxing)
*   **Goal:** Try a complex refactor without risking the main `main` branch.
*   **Path:**
    1.  User runs `gemini-toolbox --profile ~/.gemini-profiles/experiment`.
    2.  This uses a clean configuration profile (isolated history).
    3.  User performs various operations. If satisfied, they push the changes.
    4.  If not, they simply delete the profile or the container.
*   **Outcome:** Clean separation of experimental work from the daily stable environment.
