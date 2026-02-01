# Gemini CLI Toolbox

[![CI](https://github.com/Jsebayhi/gemini-cli-toolbox/actions/workflows/ci.yml/badge.svg)](https://github.com/Jsebayhi/gemini-cli-toolbox/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/jsebayhi/gemini-cli-toolbox)](https://hub.docker.com/r/jsebayhi/gemini-cli-toolbox)

**GitHub Repository:** [Jsebayhi/gemini-cli-toolbox](https://github.com/Jsebayhi/gemini-cli-toolbox) | **Docker Hub:** [jsebayhi/gemini-cli-toolbox](https://hub.docker.com/r/jsebayhi/gemini-cli-toolbox)

> **A zero-config, secure sandbox for the Gemini CLI.** Keep your AI agent fully integrated with your development environment while protecting your host.
> 
> *   **🚀 Zero Config:** No Node.js, Python, or SDK setup required on your host. Just run the script.
> *   **🛡️ Secure Sandbox:** Just as the agent cannot edit files outside your project, any command/script run by the agent is trapped in the container, guaranteeing no side effects outside your project folder.
> *   **💻 VS Code Companion:** Native integration with your host IDE for context and diffs.
> *   **🐳 Docker-Powered:** Extends the agent to any language. Build and test projects (Rust, PHP) using your host's Docker images, saving bandwidth and setup time.
> *   **📦 Persistent Caching:** Mounts your host's `~/.m2`, `~/.gradle`, and `~/.npm` caches for instant builds.
> *   **📱 Remote Access:** Code from your phone via Tailscale VPN.
> *   **🔑 Multi-Profile:** Switch seamlessly between personal, work, and bot accounts using different config dirs.

**📅 Auto-Updates:** Images are rebuilt automatically every Friday morning (UTC) to include the latest `@google/gemini-cli` release.

## Quick Start

### 1. Install the Wrapper
The `gemini-toolbox` script handles the complex Docker flags (networking, mounts, auth) for you.

```bash
# Clone the repo (or just download the script)
git clone https://github.com/Jsebayhi/gemini-cli-toolbox.git
cd gemini-cli-toolbox

# Add to your PATH (Optional)
ln -s $(pwd)/bin/gemini-toolbox ~/.local/bin/gemini-toolbox
```

### 2. Run
```bash
# Start an interactive chat
gemini-toolbox

# Run a one-shot query
gemini-toolbox "Explain the code in this directory"

# Execute a prompt and stay in interactive mode
gemini-toolbox -i "Help me refactor this project"
```

### 3. Update
To keep your sandbox fresh with the latest Gemini features:

```bash
gemini-toolbox update
```

**Note:** If your local image is older than 7 days, the script will gently remind you to update.

## Features

### 🖥️ VS Code Companion Mode
This Docker wrapper supports the **Gemini CLI Companion** extension natively.
1.  Open VS Code in your project folder.
2.  Run `gemini-toolbox -i "/ide status"` from the Integrated Terminal.
3.  **It just works.** The container connects to your host IDE to read context and diff files.

### 🐳 Docker-out-of-Docker
The container connects to your **host's Docker Daemon** (via `/var/run/docker.sock`). This gives the agent the power to:
*   Start databases (e.g., `docker run -d -p 5432:5432 postgres`).
*   Build images (e.g., `docker build .`).
*   Run integration tests using `docker-compose`.

#### ✅ Benefits: Shared Cache
Because it talks to your host daemon, the agent **shares your host's image library**.
*   **Instant Builds:** If you have already built an image locally, the agent can use it immediately.
*   **Bandwidth Saver:** It doesn't need to re-download `postgres` or `node` images inside the container.

#### 🛡️ Sandbox Opt-Out
By default, Docker support is **Enabled**. This effectively gives the agent root-level control over your host's Docker environment.
If you are running untrusted scripts or want a strict sandbox, you can disable this:

```bash
# Disable Docker integration (Strict Sandbox Mode)
gemini-toolbox --no-docker
```

#### ⚠️ Limitation: Volume Mounts
The agent is running *inside* a container, but it sends commands to the *host*.
*   **Relative Paths Work:** `docker run -v ./data:/data ...` works because we mirror the project path.
*   **Absolute Paths Fail:** `docker run -v /home/gemini/cache:/cache ...` will fail because `/home/gemini` likely doesn't exist on your host.
*   **Tip:** Always use relative paths (`./`) in your `docker-compose.yml` files.

### 📱 Remote Access
Access your Gemini CLI session from your phone or tablet using integrated **Tailscale VPN** support. This works with zero host configuration, even if you are behind a corporate VPN.

#### 1. Start a Session
Run the toolbox with the `--remote` flag and your Tailscale Auth Key.
```bash
# Option 1: One-shot
gemini-toolbox --remote tskey-auth-xxxxxx

# Option 2: Environment Variable
export GEMINI_REMOTE_KEY="tskey-auth-xxxxxx"
gemini-toolbox --remote
```

This command will:
1.  Start your Gemini CLI session (isolated on the VPN).
    *   **Hostname:** `gem-{PROJECT}-{TYPE}-{ID}` (e.g., `gem-myapp-geminicli-a1b2`).
2.  **Auto-Start the Gemini Hub** (see below).

> [!WARNING]
> **VS Code Integration is disabled** when using Remote Access. This mode isolates the container's network stack for secure VPN connectivity, preventing it from talking to the host's IDE.

### 📱 Gemini Hub (Mobile Discovery)
The **Gemini Hub** is a built-in dashboard that auto-starts with your remote session. It provides a "Zero Config" way to discover and connect to your containers from a phone.

*   **URL:** `http://gemini-hub:8888` (via MagicDNS)
*   **One-Tap Access:** No need to type IP addresses. Just tap your project card.
*   **Smart Features:**
    *   **New Session Wizard:** Launch new CLI or Bash sessions directly from the web UI.
    *   **Interface Selection:** Choose between the standard AI chat (CLI) or a raw shell (Bash) for remote tasks like editing files with `vim`.
    *   **Search & Filter:** Find projects by name or type.
    *   **Persistent by Default:** The Hub stays running to facilitate switching sessions. Auto-shutdown is optional.
    *   **Smart Workspace Management:** Need to access a new folder? Just run `gemini-toolbox` with the new path. The Hub will detect it and offer to **Merge and Restart** seamlessly.
    *   **Hybrid Mode (Local Access):** If the Hub detects a session running on the *same machine*, it adds a **LOCAL** badge to the card. Click it to bypass the VPN and connect directly via `localhost` for zero latency.

#### Manual Control
```bash
# Add a new workspace to the running Hub (Hot Add)
# Triggers a Smart Restart prompt
gemini-hub --workspace /data/new-project

# Stop the Hub manually
gemini-toolbox stop-hub
```

### 🧰 Multiple Flavors
We provide two variants of the tool:

| Flag | Image Tag | Description |
| :--- | :--- | :--- |
| `(default)` | `:latest` | **Stable**. The standard Gemini CLI experience. |
| `--preview` | `:latest-preview` | **Beta**. Access the latest features from the preview branch. |

**Example:**
```bash
# Use the preview version
gemini-toolbox --preview -i "Try out the latest beta features"
```

### 🧹 Multi-Account Management
You can point the container to different configuration directories to isolate environments.

```bash
# Use your personal account
gemini-toolbox --config ~/.gemini-personal

# Use your work account
gemini-toolbox --config ~/.gemini-work
```

## Advanced Usage

### 🚀 YOLO Mode & Resuming
```bash
# Automatically accept all suggested actions (YOLO)
gemini-toolbox --yolo "Fix the linting issues"

# Resume the latest session
gemini-toolbox --resume latest
```

### 🐚 Bash Mode & Scripting
You can bypass the Gemini CLI entirely and use the container as a clean, disposable shell.

```bash
# Drop into a bash shell inside the container
gemini-toolbox --bash

# Execute a single bash command
gemini-toolbox --bash -c "echo 'Hello from inside Docker' && ls -la"
```

### 📂 Custom Volume MountS
Use `-v` (or `--volume`) to mount additional directories from your host into the container.

```bash
gemini-toolbox -v /home/user/my-docs:/docs chat
```

### 👤 Configuration Profiles (Advanced)
You can maintain separate environments (e.g., "Work", "Personal") by using configuration profiles.

#### The `--profile` Flag
Use `--profile` to point to a directory acting as a **Workspace Root**. This keeps your config data isolated from your user files.

```bash
gemini-toolbox --profile ~/.gemini-profiles/work chat
```

**Structure:**
```text
~/.gemini-profiles/work/
├── extra-args          # Persistent flags (e.g., --volume ...)
├── .gemini/            # Auto-generated: stores history, cookies, and keys
└── secrets/            # Your private files
```

#### The `--config` Flag (Legacy/Simple)
Use `--config` if you just want to point to a standard configuration folder (without nesting).

```bash
gemini-toolbox --config ~/.old-gemini chat
```

#### Persistent Settings (`extra-args`)
**Only supported in Profile Mode (`--profile`).** Instead of typing `-v` or `--preview` every time, you can put them in an `extra-args` file.

**Example `extra-args`:**
```text
# Mount my work-specific documents
--volume "/mnt/data/work-docs:/docs"
```

---

### 📱 Remote Access (VPN)
Access your Gemini CLI session from your phone or tablet using integrated **Tailscale VPN** support.

### 📜 Persistent Bash History
To keep your command history across container restarts, mount your history file.

```bash
# Persist .bash_history
gemini-toolbox \
  -v ~/.gemini_bash_history:/home/gemini/.bash_history \
  --bash
```

## Manual Usage (Without the Script)
If you prefer running raw Docker commands, you must replicate the arguments yourself to enable VS Code integration.

```bash
docker run --rm -it \
  --net=host \
  --env GEMINI_CLI_IDE_SERVER_HOST=127.0.0.1 \
  --env TERM_PROGRAM=vscode \
  --volume "$PWD:$PWD" \
  --workdir "$PWD" \
  jsebayhi/gemini-cli-toolbox:latest-stable \
  "Explain this code"
```

## License
MIT
