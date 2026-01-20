# Gemini CLI Docker

[![CI](https://github.com/Jsebayhi/gemini-cli-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/Jsebayhi/gemini-cli-docker/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/jsebayhi/gemini-toolbox)](https://hub.docker.com/r/jsebayhi/gemini-toolbox)

**Docker Hub:** [jsebayhi/gemini-toolbox](https://hub.docker.com/r/jsebayhi/gemini-toolbox)

> **Securely sandbox the Gemini CLI** to execute scripts and commands without risking host integrity. Manage multiple accounts on one machine with full **VS Code Companion Mode** support. Includes shared dependency caches for instant project compilation (Java, Go, Node).
> **zero-config, secure sandbox** for safe experimentation. *Incoming: Native remote access.*

## Why use this?

*   🔒 **Sandboxed & Secure:** Don't let AI-generated scripts run directly on your OS. Isolate them in a disposable container.
*   ⚡ **VS Code Integration:** Connects natively to your host IDE. Open files, diff changes, and use the companion extension as if the CLI were installed locally.
*   🚀 **Zero Config:** No Node.js, Python, or SDK setup required on your host. Just run the script.
*   📦 **Persistent Caching:** Mounts your host's `~/.m2`, `~/.gradle`, and `~/.npm` caches so builds inside the container are instant.
*   🔑 **Multi-Account:** Easily switch between different `.gemini` configurations for personal and work accounts.

## Quick Start

### 1. Install the Wrapper
The `gemini-docker` script handles the complex Docker flags (networking, mounts, auth) for you.

```bash
# Clone the repo (or just download the script)
git clone https://github.com/Jsebayhi/gemini-cli-docker.git
cd gemini-cli-docker

# Add to your PATH (Optional)
ln -s $(pwd)/bin/gemini-docker ~/.local/bin/gemini-docker
```

### 2. Run
```bash
# Start an interactive chat
gemini-docker

# Run a one-shot query
gemini-docker "Explain the code in this directory"

# Execute a prompt and stay in interactive mode
gemini-docker -i "Help me refactor this project"
```

## Features

### 🖥️ VS Code Companion Mode
This Docker wrapper supports the **Gemini CLI Companion** extension natively.
1.  Open VS Code in your project folder.
2.  Run `gemini-docker -i "/ide status"` from the Integrated Terminal.
3.  **It just works.** The container connects to your host IDE to read context and diff files.

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
gemini-docker --preview -i "Try out the latest beta features"

# Use the full stack for compiling Java/Go code
gemini-docker --full "Run the tests in this Java project"
```

### 🧹 Multi-Account Management
You can point the container to different configuration directories to isolate environments.

```bash
# Use your personal account
gemini-docker --config ~/.gemini-personal

# Use your work account
gemini-docker --config ~/.gemini-work
```

## Advanced Usage

### 🚀 YOLO Mode & Resuming
```bash
# Automatically accept all suggested actions (YOLO)
gemini-docker --yolo "Fix the linting issues"

# Resume the latest session
gemini-docker --resume latest
```

### 🐚 Bash Mode & Scripting
You can bypass the Gemini CLI entirely and use the container as a clean, disposable shell.

```bash
# Drop into a bash shell inside the container
gemini-docker --bash

# Execute a single bash command
gemini-docker --bash -c "echo 'Hello from inside Docker' && ls -la"
```

### 📂 Custom Volume Mounts
Use `-v` (or `--volume`) to mount additional directories from your host into the container.

```bash
# Mount /opt/data on host to /data in container
gemini-docker -v /opt/data:/data --bash -c "ls /data"
```

### 📜 Persistent Bash History
To keep your command history across container restarts, mount your history file.

```bash
# Persist .bash_history
gemini-docker \
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
  jsebayhi/gemini-toolbox:latest \
  "Explain this code"
```

## License
MIT