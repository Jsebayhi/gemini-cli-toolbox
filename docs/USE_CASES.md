# Gemini CLI Toolbox: Use Case Catalog

This document outlines the diverse ways you can utilize the Gemini CLI Toolbox to enhance your development workflow. From daily coding to mobile management and DevOps automation, the toolbox adapts to your needs.

---

## 1. The Daily Driver (VS Code Companion)
**Persona:** Full-time Developer
**Goal:** Seamless AI assistance inside the IDE.

By running the toolbox inside VS Code's integrated terminal, you get context-aware assistance. The container mounts your current project and communicates with the IDE extension.

```bash
# In VS Code Terminal
gemini-toolbox
```
*   **Workflow:** "Refactor this function", "Explain the selected code", "Fix the linting errors in this file".
*   **Advantage:** Zero setup on the host machine; keeps your node_modules/python env clean.

## 2. The Mobile Commander (iPad/Phone)
**Persona:** Digital Nomad / On-Call Engineer
**Goal:** Code or fix bugs while away from the desk.

Use the **Gemini Hub** to access your session from anywhere via Tailscale.

```bash
# On your Desktop
gemini-toolbox --remote tskey-auth-xxxxxx
```
*   **Workflow:** Open `http://gemini-hub:8888` on your phone. Tap your project. You now have a full terminal with the Gemini agent.
*   **Advantage:** Full coding power on a tablet without SSH apps or complex setups.

## 3. The Polyglot Builder (Docker-Powered)
**Persona:** Java/Scala/Go/Rust Developer
**Goal:** Build and test any language without installing SDKs on your host.

The toolbox connects to your host's Docker daemon. Instead of heavy images with pre-installed SDKs, the agent can use Docker to run the appropriate build tools for your project.

```bash
gemini-toolbox "Run the tests for this Rust project using cargo"
```
*   **Workflow:** The agent can run `docker run --rm -v $(pwd):/app -w /app rust:latest cargo test`.
*   **Advantage:** Keeps your host free of multiple SDK versions and build tools. It leverages your host's Docker cache for fast image reuse.

## 4. The DevOps Architect (Docker-out-of-Docker)
**Persona:** SRE / Platform Engineer
**Goal:** Manage containers and infrastructure.

The toolbox connects to your host's Docker socket. The agent can control your Docker daemon.

```bash
gemini-toolbox "Spin up a Postgres container and a Redis container for testing"
```
*   **Workflow:** The agent writes a `docker-compose.yml` and runs `docker compose up -d`.
*   **Advantage:** The agent can act on the infrastructure, not just talk about it.

## 5. The Log Analyzer (Piping & Scripting)
**Persona:** Sysadmin
**Goal:** Analyze logs or errors instantly.

You can pipe data into the toolbox for a one-shot analysis.

```bash
cat /var/log/syslog | tail -n 50 | gemini-toolbox "Identify the root cause of these errors"
```
*   **Workflow:** Quick triage of system state.
*   **Advantage:** fast, terminal-native integration.

## 6. The Isolated Auditor (Security Sandbox)
**Persona:** Security Researcher
**Goal:** Analyze untrusted code safely.

If you downloaded a suspicious repo, you don't want an AI agent executing code on your host. Use the **Strict Sandbox** mode.

```bash
gemini-toolbox --no-docker --no-ide
```
*   **Workflow:** "Explain what this obfuscated script does."
*   **Advantage:** The agent is trapped in the container. It cannot access your host's Docker daemon to break out, and network access can be restricted.

## 7. The Persona Switcher (Multi-Profile)
**Persona:** Freelancer / Consultant
**Goal:** Keep client contexts separate.

Use configuration directories to maintain separate histories, prompts, and login sessions for different contexts.

```bash
# For Client A
gemini-toolbox --config ~/.gemini-client-a

# For Personal Projects
gemini-toolbox --config ~/.gemini-personal
```
*   **Workflow:** Switching contexts without polluting command history.
*   **Advantage:** Clean separation of concerns.

## 8. The Early Adopter (Preview Channel)
**Persona:** Gemini Enthusiast
**Goal:** Test the latest features before they are stable.

Google releases updates frequently. The toolbox builds a preview image every week.

```bash
gemini-toolbox --preview
```
*   **Workflow:** Trying out new beta commands or capabilities.
*   **Advantage:** Access to bleeding-edge features without breaking your stable setup.

## 9. The Headless Server (Remote Workspace)
**Persona:** Cloud Developer
**Goal:** A persistent workspace in the cloud.

Run the toolbox on a VPS (EC2/Droplet) and connect to it from your laptop via the Hub.

```bash
# On Server (inside a tmux or systemd service)
gemini-toolbox --remote $TS_KEY
```
*   **Workflow:** You connect via VPN. The session stays alive even if you disconnect.
*   **Advantage:** Long-running tasks, high-bandwidth environment, accessible from any device.

## 10. The Git Librarian
**Persona:** Open Source Maintainer
**Goal:** Automate documentation and changelogs.

Use the agent to generate commit messages or update docs based on changes.

```bash
# Generate a commit message for staged changes
git diff --staged | gemini-toolbox "Write a semantic commit message for these changes"
```
*   **Workflow:** Automating the tedious parts of version control.
*   **Advantage:** Consistency and speed.

## 11. The Autonomous Agent (Bot)
**Persona:** Developer / Automation Engineer
**Goal:** Run complex tasks in the background without intervention.

Launch a session with a specific task. The agent will execute the task and can either exit or stay open for you to review.

```bash
# Launch from the Hub UI
# 1. Open the Launch Wizard
# 2. Select project and profile
# 3. Enter task: "Refactor the authentication logic to use JWT"
# 4. Uncheck 'Interactive' if you want it to exit after finishing.
```
*   **Workflow:** Delegating long-running refactors or documentation updates.
*   **Advantage:** Multi-tasking; the bot works in its own container while you work on other features.