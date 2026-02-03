# 🗺️ Gemini CLI Toolbox: User Guide & Use Cases

This document describes standard "User Paths" or "Journeys" when using the project. It outlines the diverse ways you can utilize the Gemini CLI Toolbox to enhance your development workflow, from daily coding to mobile management and DevOps automation.

---

## 1. The Daily Driver (VS Code Companion)
Use the toolbox as your primary AI assistant directly inside VS Code. It automatically connects to the companion extension to read your editor context and apply diffs.

```bash
# In VS Code Terminal
gemini-toolbox
```

**Step-by-Step Journey:**
1.  User opens a terminal in VS Code.
2.  Runs `gemini-toolbox`.
3.  The container starts, automatically detects the VS Code environment, and connects to the host's Companion Extension.
4.  User types: `"Refactor the current file to use async/await"`.
5.  Gemini reads the context from the IDE, generates a diff, and applies it.
6.  User reviews and commits.

*   **Advantage:** Zero setup on the host machine; keeps your node_modules/python env clean.

---

## 2. The Mobile Commander (Remote Access)
Code, debug, or fix production issues from your phone or tablet via VPN. The **Gemini Hub** provides a full terminal interface accessible from anywhere.

```bash
# On your Desktop
gemini-toolbox --remote tskey-auth-xxxxxx
```

**Step-by-Step Journey:**
1.  User starts a remote session from the desktop before leaving: `gemini-toolbox --remote`.
2.  Later, from a phone/tablet, the user opens `http://gemini-hub:8888`.
3.  User taps the active project card.
4.  A web terminal opens. User interacts with Gemini to diagnose the issue.
5.  **Bonus:** User needs to edit a config file manually. They launch a new **Bash** session from the Hub's "New Session" wizard and use `vim` in the browser.

*   **Advantage:** Full desktop-class development power on any mobile device.

---

## 3. The Autonomous Agent (Bot)
Delegate complex, long-running tasks to a background bot while you focus on other work.

**Step-by-Step Journey:**
1.  User opens the Gemini Hub.
2.  User clicks "+ New Session" and selects a project.
3.  In the "Initial Task" field, they type: `"Search the codebase for TODOs and create a report in docs/TODO_REPORT.md"`.
4.  They uncheck **Interactive** and click **Launch**.
5.  The Hub starts a detached container. Gemini executes the task in the background.
6.  User checks the Hub logs later to confirm completion.

*   **Advantage:** Multi-tasking; the bot works in its own container while you work on other features.

---

## 4. The Polyglot Builder (Docker-Powered)
Build and test projects in any language (Rust, Go, Python) without cluttering your host machine with SDKs. The agent uses your host's Docker engine to run the necessary tools.

```bash
gemini-toolbox "Run the tests for this Rust project using cargo"
```
*   **Workflow:** The agent can run `docker run --rm -v $(pwd):/app -w /app rust:latest cargo test`.
*   **Advantage:** Keeps your host free of multiple SDK versions and build tools. It leverages your host's Docker cache for fast image reuse.

---

## 5. The DevOps Architect (Docker-out-of-Docker)
Manage your host's Docker containers and infrastructure using natural language.

```bash
gemini-toolbox "Spin up a Postgres container and a Redis container for testing"
```
*   **Workflow:** The agent writes a `docker-compose.yml` and runs `docker compose up -d`.
*   **Advantage:** The agent can act on the infrastructure, not just talk about it.

---

## 6. The Isolated Auditor (Security Sandbox)
Safely analyze untrusted code or repositories in a strictly isolated sandbox. The agent is trapped in the container with no access to your host's Docker daemon or IDE.

```bash
gemini-toolbox --no-docker --no-ide
```

**Step-by-Step Journey:**
1.  User clones the repo into a temporary folder.
2.  User runs `gemini-toolbox --no-docker --no-ide`.
3.  This ensures the agent is strictly trapped in the container with no access to the host's Docker socket or IDE.
4.  User asks: `"Analyze this shell script for any malicious network calls"`.

*   **Outcome:** Secure, isolated analysis of untrusted code.

---

## 7. The Experimenter (Multi-Profile)
Switch contexts instantly between work, personal, and experimental profiles. Each profile maintains its own history and configuration.

```bash
# For Client A
gemini-toolbox --profile ~/.gemini-profiles/client-a
```

**Step-by-Step Journey:**
1.  User runs `gemini-toolbox --profile ~/.gemini-profiles/experiment`.
2.  This uses a clean configuration profile (isolated history).
3.  User performs various operations. If satisfied, they push the changes.
4.  If not, they simply delete the profile or the container.

*   **Advantage:** Clean separation of experimental work from the daily stable environment.

---

## 8. The Log Analyzer (Piping & Scripting)
Pipe system logs or error dumps directly into the AI for instant analysis.

```bash
cat /var/log/syslog | tail -n 50 | gemini-toolbox "Identify the root cause of these errors"
```
*   **Advantage:** fast, terminal-native integration.

---

## 9. The Git Librarian
Automate git workflows like generating commit messages or changelogs.

```bash
# Generate a commit message for staged changes
git diff --staged | gemini-toolbox "Write a semantic commit message for these changes"
```
*   **Advantage:** Consistency and speed.