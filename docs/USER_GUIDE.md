# 🗺️ Gemini CLI Toolbox: User Guide

Welcome to the Gemini CLI Toolbox. This guide explores the diverse ways you can use this tool to enhance your workflow, from daily coding assistance to managing infrastructure and working remotely.

---

## 1. Seamless VS Code Integration
**The Scenario:** You are deep in a complex refactor. You need AI help, but you don't want to constantly copy-paste code into a web browser, and you certainly don't want to clutter your host machine with CLI dependencies.

**The Solution:** Run the toolbox directly inside VS Code's integrated terminal.
```bash
gemini-toolbox
```
It automatically detects your environment and connects to the **Gemini CLI Companion** extension. You can simply say *"Refactor the selected code to use async/await"* or *"Explain this file"*. The agent sees exactly what you see and can even apply diffs directly to your files.

---

## 2. Coding from Anywhere (Remote Access)
**The Scenario:** A production issue hits while you're away from your desk. You only have your phone or tablet, but you need full terminal access to your dev machine to fix it.

**The Solution:** Leave your session running in "Remote Mode" on your desktop.
```bash
gemini-toolbox --remote
```
Then, connect from anywhere using the **Gemini Hub** (`http://gemini-hub:8888`) over your Tailscale VPN. You get a full, responsive terminal on your mobile device, allowing you to debug, run commands, or even edit files with `vim` just as if you were sitting at your keyboard.

---

## 3. Autonomous Assistants (Bots)
**The Scenario:** You have a tedious, long-running task—like finding all "TODO" comments in a legacy codebase and summarizing them in a report—that distracts you from your main work.

**The Solution:** Delegate it. Open the **Gemini Hub**, click **New Session**, and enter your task:
> *"Scan the codebase for TODOs and create a prioritized report in docs/TECHNICAL_DEBT.md"*

Uncheck "Interactive" and click Launch. The toolbox spins up a dedicated container to handle this chore in the background, freeing you to focus on feature work.

---

## 4. The Universal Builder (No SDKs Required)
**The Scenario:** You need to build or test a project in a language you don't use often (e.g., Rust, Go, Python) and you don't want to install the entire toolchain on your host.

**The Solution:** Let the agent use Docker.
```bash
gemini-toolbox "Run the tests for this Rust project"
```
Because the toolbox shares your host's Docker socket, the agent can spin up a temporary `rust` container, mount your code, and run `cargo test`. It uses your host's image cache, so it's instant, but your host OS remains clean of SDK clutter.

---

## 5. Infrastructure as Conversation
**The Scenario:** You need a Postgres database and a Redis cache to run integration tests, but you don't want to write the `docker-compose.yml` file from scratch.

**The Solution:** Just ask for it.
```bash
gemini-toolbox "Spin up a Postgres container and a Redis container for testing"
```
The agent understands your infrastructure needs and can directly interact with the Docker daemon to start, stop, and manage services for you.

---

## 6. The Safety Sandbox
**The Scenario:** You've downloaded a GitHub repository from an unknown source to audit it, but you're worried about running its code or even letting an AI execute parts of it on your machine.

**The Solution:** Lock it down.
```bash
gemini-toolbox --no-docker --no-ide
```
This launches **Strict Sandbox Mode**. The agent is trapped inside the container with **no access** to your host's Docker daemon or your IDE. It can read and analyze the files in the folder you mounted, but it cannot escape or affect your system configuration.

---

## 7. Context Switching (Profiles)
**The Scenario:** You work on both personal projects and confidential client work. You need to ensure that your command history, secret keys, and project contexts never mix.

**The Solution:** Use Profiles.
```bash
# Morning: Client Work
gemini-toolbox --profile ~/.gemini-profiles/acme-corp

# Evening: Hobby Project
gemini-toolbox --profile ~/.gemini-profiles/hobby
```
Each profile has its own isolated history, cookies, and configuration. Switching contexts is as simple as changing a flag.

---


## 8. Instant Log Analysis
**The Scenario:** You are staring at a massive, cryptic error log on a server and need immediate insight.

**The Solution:** Pipe it.
```bash
cat /var/log/syslog | tail -n 50 | gemini-toolbox "Identify the root cause of these errors"
```
The toolbox accepts standard input, making it a powerful addition to your Unix piping workflows.

---

## 9. Automating Git
**The Scenario:** You've finished a feature but dread writing the detailed commit message or changelog entry.

**The Solution:** Automate the toil.
```bash
git diff --staged | gemini-toolbox "Write a semantic commit message for these changes"
```
The agent analyzes your actual code changes and generates a precise, professional commit message for you to review.

---

## 10. Risk-Free Experimentation (Worktrees)
**The Scenario:** You want to try a radical refactor or test a new library, but you don't want to mess up your current workspace or deal with stashing changes.

**The Solution:** Launch an **Ephemeral Worktree**.
```bash
# Create a named worktree 'refactor-auth' and start working
gemini-toolbox --worktree --name refactor-auth "Refactor the authentication logic"
```
The toolbox automatically:
1.  Creates a new, isolated folder for this task.
2.  Creates a Git branch for you.
3.  Launches the agent in that clean environment.

Your main working directory remains untouched. If the experiment fails, just delete the branch. If it succeeds, merge it back.


---

## 11. Multi-Session Isolation (Collaboration)
**The Scenario:** You are working on a complex feature in a worktree and you want to have one agent running a long-task (e.g., writing tests) in the background while you have an interactive chat in another terminal to discuss architectural choices.

**The Solution:** Launch a second session in the same worktree.
```bash
# Terminal 1: Background task
gemini-toolbox --worktree --name my-feature "Write exhaustive unit tests for app/services" &

# Terminal 2: Interactive session in the SAME worktree
gemini-toolbox --worktree --name my-feature
```
Because the toolbox detects that the worktree `my-feature` already exists, it simply joins the existing isolated environment without creating new branches. This allows for powerful human-agent or agent-agent collaboration in a single, clean workspace.

---

## 12. Resilient Sessions (Reconnection)
**The Scenario:** You are in the middle of a session when your terminal app crashes, or you accidentally close the window.

**The Solution:** Reconnect seamlessly.
By default, all sessions are wrapped in a multiplexer (`tmux`). This means the process stays alive even if the window closes.

1.  List active sessions (e.g., via `docker ps` or the Hub).
2.  Reconnect using the ID:
    ```bash
    gemini-toolbox connect gem-my-project-geminicli-1234abcd
    ```

You will be placed exactly where you left off.

**Opt-out:** If you specifically need a raw process (e.g., for automated wrapping) and want to disable this protection:
```bash
gemini-toolbox --no-tmux
```
*Note: Sessions started with `--no-tmux` cannot be reconnected to if the terminal crashes.*

---

## 13. Lifecycle Management (Stop)
**The Scenario:** You've finished your work or realized a background bot is going in the wrong direction, and you want to clean up resources without diving into Docker commands.

**The Solution:** Use the `stop` command.
```bash
# Stop a specific session by ID
gemini-toolbox stop gem-my-project-geminicli-abc12345

# Stop a session by project name (works if only one session for that project is active)
gemini-toolbox stop my-project
```
If multiple sessions are running for the same project, the toolbox will safely refuse to stop them and list the active IDs for you to choose from. You can also stop any session with a single click from the **Gemini Hub** dashboard.
