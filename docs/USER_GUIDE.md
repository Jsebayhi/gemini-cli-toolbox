# 🗺️ Gemini CLI Toolbox: User Guide & Use Cases

This document describes standard "User Paths" or "Journeys" when using the project. It outlines the diverse ways you can utilize the Gemini CLI Toolbox to enhance your development workflow, from daily coding to mobile management and DevOps automation.

---

## 1. The Daily Driver (VS Code Companion)
**Persona:** Full-time Developer
**Goal:** Seamless AI assistance inside the IDE.

By running the toolbox inside VS Code's integrated terminal, you get context-aware assistance. The container mounts your current project and communicates with the IDE extension.

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
**Persona:** Digital Nomad / On-Call Engineer
**Goal:** Code or fix bugs while away from the desk.

Use the **Gemini Hub** to access your session from anywhere via Tailscale.

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
**Persona:** Developer / Automation Engineer
**Goal:** Run complex tasks in the background without intervention.

Launch a session with a specific task. The agent will execute the task and can either exit or stay open for you to review.

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
**Persona:** Java/Scala/Go/Rust Developer
**Goal:** Build and test any language without installing SDKs on your host.

The toolbox connects to your host's Docker daemon. Instead of heavy images with pre-installed SDKs, the agent can use Docker to run the appropriate build tools for your project.

```bash
gemini-toolbox "Run the tests for this Rust project using cargo"
```
*   **Workflow:** The agent can run `docker run --rm -v $(pwd):/app -w /app rust:latest cargo test`.
*   **Advantage:** Keeps your host free of multiple SDK versions and build tools. It leverages your host's Docker cache for fast image reuse.

---

## 5. The DevOps Architect (Docker-out-of-Docker)
**Persona:** SRE / Platform Engineer
**Goal:** Manage containers and infrastructure.

The toolbox connects to your host's Docker socket. The agent can control your Docker daemon.

```bash
gemini-toolbox "Spin up a Postgres container and a Redis container for testing"
```
*   **Workflow:** The agent writes a `docker-compose.yml` and runs `docker compose up -d`.
*   **Advantage:** The agent can act on the infrastructure, not just talk about it.

---

## 6. The Isolated Auditor (Security Sandbox)
**Persona:** Security Researcher
**Goal:** Analyze a suspicious third-party repository safely.

If you downloaded a suspicious repo, you don't want an AI agent executing code on your host. Use the **Strict Sandbox** mode.

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
**Persona:** Freelancer / Consultant
**Goal:** Try a complex refactor or keep client contexts separate.

Use configuration directories to maintain separate histories, prompts, and login sessions for different contexts.

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
**Persona:** Sysadmin
**Goal:** Analyze logs or errors instantly.

You can pipe data into the toolbox for a one-shot analysis.

```bash
cat /var/log/syslog | tail -n 50 | gemini-toolbox "Identify the root cause of these errors"
```
*   **Advantage:** fast, terminal-native integration.

---

## 9. The Git Librarian
**Persona:** Open Source Maintainer
**Goal:** Automate documentation and changelogs.

Use the agent to generate commit messages or update docs based on changes.

```bash
# Generate a commit message for staged changes
git diff --staged | gemini-toolbox "Write a semantic commit message for these changes"
```
*   **Advantage:** Consistency and speed.
