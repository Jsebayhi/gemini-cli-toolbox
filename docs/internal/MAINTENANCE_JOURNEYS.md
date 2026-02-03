# 🛠️ Internal Maintenance Journeys (QA Matrix)

This document tracks the supported user paths and variants. It serves as a checklist for regression testing.

## 🧪 Test Matrix

### 1. Core Entry Points (The Journeys)
These represent the fundamental ways a user starts a session. Every update must pass these.

| ID | Journey | Command | Expected Result |
|:---|:---|:---|:---|
| **J1** | **Local Default** | `gemini-toolbox` | Interactive CLI in current folder. Uses `~/.gemini`. |
| **J2** | **Local Profile** | `gemini-toolbox --profile /tmp/prof` | Interactive CLI. Uses `/tmp/prof/.gemini`. |
| **J3** | **Remote Default** | `gemini-toolbox --remote` | CLI starts. Hub starts. Accessible via VPN. |
| **J4** | **Remote Profile** | `gemini-toolbox --remote --profile /tmp/prof` | Remote CLI using isolated profile storage. |
| **J5** | **Hub Launch** | Hub UI > New Session > Launch | New container starts from Web UI. |

### 2. Feature Modifiers (The Flags)
These flags can technically apply to most Journeys. Verify they trigger the correct internal logic.

| ID | Modifier | Flag | Validation Check |
|:---|:---|:---|:---|
| **M1** | **Strict Sandbox** | `--no-docker` | Run `docker ps` inside container -> Fails (Socket missing). |
| **M2** | **No IDE** | `--no-ide` | `env | grep TERM_PROGRAM` -> Empty. |
| **M3** | **Bash Mode** | `--bash` | Entrypoint is `/bin/bash`, not `gemini`. |
| **M4** | **Preview** | `--preview` | Image tag is `...:latest-preview`. |
| **M5** | **One-Shot** | `"task"` (Positional) | Agent runs task and exits. |
| **M6** | **Interactive** | `-i "task"` | Agent runs task and stays open. |
| **M7** | **Legacy Config** | `--config /tmp/conf` | Mounts directly to `/home/gemini/.gemini` (No nesting). |

### 3. Session Transitions
Actions performed on *existing* sessions.

| ID | Action | Command | Validation |
|:---|:---|:---|:---|
| **T1** | **Attach (CLI)** | `gemini-toolbox connect <id>` | Connects to `tmux` session. |
| **T2** | **Attach (Bash)** | `gemini-toolbox connect <id>` | Connects to `bash` process (or starts new one). |
| **T3** | **Hub Restart** | Launch J1 in `/dirA`, then J1 in `/dirB`. | Hub detects new root and performs Smart Restart. |
| **T4** | **Stop Hub** | `gemini-toolbox stop-hub` | `gemini-hub-service` container is removed. |

### 4. Edge Scenarios
| ID | Scenario | Details |
|:---|:---|:---|
| **E1** | **Profile Persistence** | Define `extra-args` in profile root. Launch J2. Verify args are applied. |
| **E2** | **Hub Bot** | Launch "Autonomous Bot" from Hub UI. Verify M6 behavior remotely. |
| **E3** | **Hybrid Access** | Access Hub via `localhost:8888`. Verify "Local" routing. |