# Gemini CLI Toolbox

[![CI](https://github.com/Jsebayhi/gemini-cli-toolbox/actions/workflows/ci.yml/badge.svg)](https://github.com/Jsebayhi/gemini-cli-toolbox/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/jsebayhi/gemini-cli-toolbox)](https://hub.docker.com/r/jsebayhi/gemini-cli-toolbox)

**GitHub Repository:** [Jsebayhi/gemini-cli-toolbox](https://github.com/Jsebayhi/gemini-cli-toolbox) | **Docker Hub:** [jsebayhi/gemini-cli-toolbox](https://hub.docker.com/r/jsebayhi/gemini-cli-toolbox)

> **Securely sandbox the Gemini CLI** to execute scripts and commands without risking host integrity. Manage multiple accounts on one machine with full **VS Code Companion Mode** support. Includes shared dependency caches for instant project compilation (Java, Go, Node).
> **zero-config, secure sandbox** for safe experimentation with **Native Remote Access (Experimental)** via Tailscale.

**📅 Auto-Updates:** Images are rebuilt automatically every Friday morning (UTC) to include the latest `@google/gemini-cli` release.

## Why use this?

*   🔒 **Sandboxed & Secure:** Don't let AI-generated scripts run directly on your OS. Isolate them in a disposable container.
*   📱 **Remote Access (Experimental):** Code from your phone or tablet anywhere. Integrated VPN support lets you safely access your dev environment on the go.
*   ⚡ **VS Code Integration:** Connects natively to your host IDE. Open files, diff changes, and use the companion extension as if the CLI were installed locally.
*   🚀 **Zero Config:** No Node.js, Python, or SDK setup required on your host. Just run the script.
*   📦 **Persistent Caching:** Mounts your host's `~/.m2`, `~/.gradle`, and `~/.npm` caches so builds inside the container are instant.
*   🐳 **Docker Integration:** Run `docker` and `docker-compose` commands directly from the agent. Supports building images and running databases.
*   🔑 **Multi-Account:** Easily switch between different `.gemini` configurations for personal and work accounts.

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

> [!TIP]
> **Retrocompatibility:** For existing users, the `gemini-docker` command is still available as a symbolic link to `gemini-toolbox`. Both commands are interchangeable.

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

### 📱 Remote Access (Experimental)
Access your Gemini CLI session from your phone or tablet using integrated **Tailscale VPN** support. This works with zero host configuration, even if you are behind a corporate VPN.

1.  **Get a Key:** Go to [Tailscale Settings > Keys](https://login.tailscale.com/admin/settings/keys). Generate a **Reusable Auth Key**.
2.  **Run:** Pass the key or set the environment variable.
    ```bash
    # Option 1: One-shot
    gemini-toolbox --remote tskey-auth-xxxxxx

    # Option 2: Environment Variable
    export GEMINI_REMOTE_KEY="tskey-auth-xxxxxx"
    gemini-toolbox --remote
    ```
3.  **Connect:** Open the **Tailscale App** on your phone. You will see a new device named `gemini-<project>-<id>`. Access it at `http://<IP>:3000`.

**✨ Real-time Mirroring:** Desktop and phone share the exact same session via `tmux`. What you type on one appears instantly on the other.

> [!WARNING]
> **VS Code Integration is disabled** when using Remote Access. This mode isolates the container's network stack for secure VPN connectivity, preventing it from talking to the host's IDE.

### 🧰 Multiple Flavors
We provide three variants of the tool:

| Flag | Image Tag | Description |
| :--- | :--- | :--- |
| `(default)` | `:latest` | **Stable**. The standard Gemini CLI experience. |
| `--preview` | `:latest-preview` | **Beta**. Access the latest features from the preview branch. |
| `--full` | `:latest-full` | **Batteries Included**. Pre-installed Java, Go, Python, and Node.js runtimes for executing complex code. |

**Example:**
```bash
# Use the preview version
gemini-toolbox --preview -i "Try out the latest beta features"

# Use the full stack for compiling Java/Go code
gemini-toolbox --full "Run the tests in this Java project"
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

### 📂 Custom Volume Mounts
Use `-v` (or `--volume`) to mount additional directories from your host into the container.

```bash
# Mount /opt/data on host to /data in container
gemini-toolbox -v /opt/data:/data --bash -c "ls /data"
```

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