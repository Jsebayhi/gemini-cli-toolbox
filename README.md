# 🤖 Gemini CLI Toolbox

[![CI](https://github.com/Jsebayhi/gemini-cli-toolbox/actions/workflows/ci.yml/badge.svg)](https://github.com/Jsebayhi/gemini-cli-toolbox/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/jsebayhi/gemini-cli-toolbox)](https://hub.docker.com/r/jsebayhi/gemini-cli-toolbox)

> **The zero-config, ultra-secure home for your Gemini AI agent.**
> Run the Gemini CLI in a Dockerized sandbox that keeps your host system clean while staying fully integrated with your tools (VS Code, Docker, VPN).

---

## ⚡ Quick Start (Under 5 Minutes)

### 1. Install the Wrapper
The `gemini-toolbox` script handles the complex Docker logic for you.

```bash
# Clone and enter the repo
git clone https://github.com/Jsebayhi/gemini-cli-toolbox.git
cd gemini-cli-toolbox

# Add to your PATH (Optional but recommended)
ln -s $(pwd)/bin/gemini-toolbox ~/.local/bin/gemini-toolbox
```

### 2. Enable Autocompletion (Optional)
```bash
source completions/gemini-toolbox.bash
source completions/gemini-hub.bash
```

### 3. Start Chatting
```bash
# Open interactive AI chat in the current folder
gemini-toolbox
```

---

## 🏗️ How it Works (The 20-Minute Deep Dive)

The Toolbox isn't just a wrapper; it's a bridge between your host and a secure execution environment.

### 🛡️ 1. Security & Sandbox
*   **Isolation:** The agent runs inside a Debian container. It **cannot** see or modify files outside the project directory you mount.
*   **Ephemeral:** Every session is clean. Use the container as a disposable playground for running experimental scripts or refactors.

### 💻 2. Developer Integration
*   **VS Code Companion:** Native support for the [Gemini CLI Companion](https://github.com/google/gemini-cli) extension. It reads your IDE context and applies diffs automatically.
*   **Docker-out-of-Docker (DooD):** The agent can run `docker` commands (build, run, compose) by talking to your host's daemon. It shares your local image cache for instant speed.
*   **Language Agnostic:** No need to install Node.js, Python, or Rust on your host. Build and test projects using the agent's internal environment or host Docker.

### 📱 3. Remote & Mobile Freedom
*   **Tailscale VPN:** Start a session with `--remote` to access it from your phone, tablet, or another PC via a secure mesh network.
*   **The Hub:** A built-in web dashboard (`http://gemini-hub:8888`) to discover and manage multiple active sessions from any device.

---

## 📚 Learning Path

Want to go deeper? Follow these guides to master the Toolbox:

1.  **[User Journeys](docs/user_path.md) (5 min):** See how components work together in real-world scenarios (Remote troubleshooting, Background bots, Security auditing).
2.  **[Use Case Catalog](docs/USE_CASES.md) (15 min):** A detailed breakdown of features for different personas (DevOps, SRE, Polyglot developers).
3.  **[Architecture Decisions (ADRs)](adr/) (20+ min):** Understand the "Why" behind the "How".

---

## 📖 Key Features & Use Cases

### 🛠️ Common Commands
| Goal | Command |
| :--- | :--- |
| **Simple Chat** | `gemini-toolbox` |
| **One-shot Task** | `gemini-toolbox "Fix the linting errors in src/"` |
| **Beta Features** | `gemini-toolbox --preview` |
| **Remote Coding** | `gemini-toolbox --remote` |
| **Disposable Shell**| `gemini-toolbox --bash` |

### 📂 Multi-Account Management
Isolate your environments using configuration profiles.
```bash
# Use a specific profile (e.g., Work vs Personal)
gemini-toolbox --profile ~/.gemini-profiles/work
```

### 🕒 Recent Paths
The Hub wizard automatically remembers your last 3 paths (stored in your browser's `localStorage`), making it effortless to jump back into a project from mobile.

---

## 🔧 Advanced Configuration

### Persistent Settings (`extra-args`)
Inside a profile directory (when using `--profile`), create a file named `extra-args` to store flags you use every time:
```text
# ~/.gemini-profiles/work/extra-args
--volume "/mnt/data/docs:/docs"
--no-ide
```

### 📜 Persistent Bash History
Keep your command history across container restarts:
```bash
gemini-toolbox -v ~/.gemini_bash_history:/home/gemini/.bash_history --bash
```

---

## 🤝 Contributing
We love contributors! If you add or modify CLI flags, please remember to update the scripts in `completions/`. See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for more details.

## 📄 License
MIT