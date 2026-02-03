# 🏗️ Architecture & Features Deep Dive

This document provides a technical breakdown of how the Gemini CLI Toolbox works under the hood. It is intended for power users, security-conscious developers, and contributors.

---

## 🛡️ 1. Security & Isolation

### The "Sandbox" Promise
The core philosophy of this toolbox is **Host Protection**. By running the agent in a container, we ensure:
*   **File System:** The agent sees *only* the project directory you explicitly mounted (`--project` or default `$PWD`). It cannot access `~/.ssh`, `/etc`, or other projects.
*   **Process Isolation:** If the agent runs `rm -rf /`, it destroys the container's filesystem, not yours.
*   **Network (Local):** The container shares the host network stack (`--net=host`). This is **required** to support the Google OAuth browser flow (which spins up a local server on varying ports to capture your login token). Strict network isolation (bridge mode) is currently only enabled when using `--remote`.

### Permission Management (`gosu`)
*   **The Problem:** Docker containers typically run as root. If the agent creates a file, it ends up owned by `root` on your host, requiring `sudo` to delete.
*   **The Solution:** The entrypoint script (`docker-entrypoint.sh`) reads your host UID/GID (passed via env vars). It uses `gosu` to drop privileges to your user level *inside* the container before executing any command.
*   **Result:** Files created by Gemini are owned by **you**.

---

## 🆔 2. Session Identity & Naming

Every time you run the toolbox, it generates a unique **Session ID** based on the following pattern:
`gem-{PROJECT_NAME}-{TYPE}-{UNIQUE_SUFFIX}`

### Consistency by Design
This ID is not just a label; it is the source of truth for session identity:
*   **Docker Container Name:** Every container is explicitly named after its Session ID. This allows commands like `gemini-toolbox connect <id>` to work reliably.
*   **Tailscale Hostname:** When running in remote mode, this same ID is used as the node's hostname on the VPN.
*   **Consistency:** The 1:1 mapping between the container name and the network identity ensures that discovery tools (like the Hub) can always resolve and connect to the correct instance.

---

## 💻 3. IDE Integration (VS Code)

### The "Companion" Protocol
The [Gemini CLI Companion](https://github.com/google/gemini-cli) extension for VS Code normally expects the CLI to run locally. We trick it into working with Docker.

1.  **Environment Variables:** The toolbox script detects if it's running inside VS Code (`TERM_PROGRAM=vscode`).
2.  **Passthrough:** It captures the extension's connection details (`GEMINI_CLI_IDE_SERVER_PORT`, `GEMINI_CLI_IDE_AUTH_TOKEN`).
3.  **The Patch:** Our Docker image includes a **patched version of the Gemini CLI** that allows it to connect to the host IDE at `127.0.0.1` (forced via `GEMINI_CLI_IDE_SERVER_HOST`) instead of expecting a local process. This bypasses the default "localhost only" security restriction of the CLI when running inside a container.

### Path Mirroring
For the extension to apply diffs, the file paths inside the container must match the file paths in VS Code.
*   **Solution:** We don't mount to `/app`. We mount the project to its **exact absolute path** (e.g., `/home/user/projects/my-app` maps to `/home/user/projects/my-app` inside the container).

---

## 🐳 3. Docker-out-of-Docker (DooD)

### Shared Daemon & The Caching Trade-off
The toolbox uses "Docker-out-of-Docker" (DooD) by mounting the host's Docker socket (`/var/run/docker.sock`) into the container. This architectural choice is driven by **resource efficiency**.

**The Primary Goal: Shared Image Cache**
Without this, each concurrent session would be isolated, forcing you to re-download the same base images (e.g., `node`, `python`, `rust`) multiple times. By sharing the host's socket, images pulled in one session are immediately available to all others and your host, saving significant bandwidth and disk space.

**The Trade-off: Reduced Isolation**
Ideally, the agent would be fully sandboxed from your host's Docker state. However, because we share the socket to achieve caching, the agent effectively gains the ability to see and manage containers running on your host.

If your use case requires a **full sandbox** where the agent is strictly forbidden from interacting with the host's Docker daemon, you should use the `--no-docker` flag.

### Capabilities
The agent can:
*   `docker ps`: See containers running on your host.
*   `docker build`: Build images using your host's engine.
*   `docker run`: Launch *sibling* containers (not child containers).

### ⚠️ Important Limitations
Because the agent controls the *Host* daemon, **Volume Mounts** are tricky.
*   **Context:** When the agent runs `docker run -v ./data:/data`, the Host Daemon resolves `./data`.
*   **Success:** Since we mirror the project path (see above), `./` inside the container resolves to the same absolute path on the host.
*   **Failure:** If the agent tries `docker run -v /tmp/container-path:/data`, it will fail because `/tmp/container-path` doesn't exist on the host.

---

## 📱 5. Remote Access & VPN

### Tailscale Integration
When you use `--remote [key]` (or simply `--remote` if the `GEMINI_REMOTE_KEY` environment variable is set), the toolbox architecture changes:
1.  **Network Isolation:** It switches from `--net=host` to `--net=bridge`.
2.  **Userspace Networking:** It starts `tailscaled` inside the container in userspace mode (`--tun=userspace-networking`).
3.  **Registration:** It registers a transient node on your Tailnet using the **Session ID** (see Section 2) as its hostname.

### The Gemini Hub
The Hub is a standalone container (`gemini-hub-service`) that acts as a discovery server and remote manager. While it usually auto-starts with `--remote`, you can also run it manually as a central dashboard.

#### 1. Discovery & Connection
*   **Mesh Discovery:** It queries the local Tailscale socket to find any active `gem-` peers on your network.
*   **Web Proxy:** It provides a Web UI to launch `ttyd` (Web Terminal) sessions connecting to those peers.
*   **Access:**
    *   **Mobile/Remote:** `http://gemini-hub:8888` (via MagicDNS)
    *   **Local Desktop:** `http://localhost:8888`

#### 2. Hybrid Mode (Localhost Optimization)
The Hub is smart enough to know where it is running.
*   **Scenario:** You are browsing the Hub from the same computer running the containers.
*   **Optimization:** Instead of routing traffic through the VPN (which adds latency), the Hub attempts to reach the container via `localhost`.
*   **Behavior:**
    *   **Priority:** If reachable, the **primary link** on the session card automatically switches to `localhost`.
    *   **Fallback:** A **"VPN"** badge appears alongside the status indicator. This allows you to explicitly choose the Tailscale IP even if local access is available.
    *   **Remote:** If you are on a different device (phone/tablet), the Hub detects `localhost` is unreachable and defaults the primary link to the VPN.

#### 3. Remote Session Management
The Hub is not just a passive list; it is an active **Remote Job Runner**.
*   **Launch Wizard:** From the Hub UI, you can start *new* sessions (CLI or Bash) in any workspace it has access to.
*   **Autonomous Bots:** You can dispatch autonomous tasks (e.g., "Refactor this module") directly from the dashboard without opening a terminal.

#### 3. Standalone Usage
You can run the Hub manually to manage your environment:
```bash
# Start Hub, scanning specific projects and profiles
gemini-hub \
  --workspace ~/projects/work \
  --workspace ~/projects/personal \
  --config-root ~/.gemini-profiles
```
*   **Smart Restart:** If you launch a session in a new folder not currently scanned by the Hub, the toolbox detects this and triggers a "Smart Restart" of the Hub to dynamically mount the new workspace.

---

## 📦 5. Caching & Persistence

To make the ephemeral container practical, we selectively persist critical data.

### Build Caches
We mount standard cache directories from your host to speed up builds:
*   `~/.m2` (Maven)
*   `~/.gradle` (Gradle)
*   `~/.npm` (Node)
*   `~/.cache/pip` (Python)
*   `~/go/pkg` (Go)

---

## 👤 6. Configuration Profiles (Multi-Account)

The toolbox supports advanced context isolation through **Configuration Profiles**. This is essential for users who manage multiple accounts (e.g., Work vs. Personal) or distinct environments.

### The `--profile` Architecture
When you run `gemini-toolbox --profile /path/to/my-profile`, the toolbox treats that directory as a **Workspace Root**, not just a simple config folder.

**Directory Structure:**
```text
/path/to/my-profile/
├── .gemini/            # [Auto-Generated] The actual home of the Gemini CLI state (history, cookies, keys).
└── extra-args          # [User-Created] A text file containing persistent flags.
```

### Separation of State and Configuration
The `--profile` flag is designed to keep your workspace organized by separating your settings from the tool's internal data:

*   **User-Managed (The Root):** The directory you pass to `--profile` is your space. You can place your `extra-args` file or other project-specific notes here.
*   **Tool-Managed (The `.gemini` folder):** The toolbox automatically creates a hidden `.gemini/` subdirectory to store history, cookies, and keys.

This nesting ensures that your configuration files are not buried among hundreds of auto-generated session and cache files, making the profile easier to manage and version control.

### Persistent Arguments (`extra-args`)
You can define persistent runtime arguments for a specific profile by creating a file named `extra-args` in the profile root.
*   **Format:** One flag per line (or space-separated).
*   **Usage:** Automatically loaded whenever you use this profile.

**Example `extra-args`:**
```bash
--no-ide
--volume "/mnt/data/work-docs:/docs"
--env "MY_API_KEY=secret"
```
