# Technical Specification: Dockerized Gemini CLI Toolbox

## 1. Product Vision
To provide a portable, containerized environment for the Google Gemini CLI that functions indistinguishably from a native installation while offering superior context management and isolation. The tool acts as both an interactive chatbot and an autonomous agent capable of operating on local projects.

## 2. Requirements Specification

### 2.1. Functional Requirements
*   **REQ-F-01 (Context Isolation):** The system must allow the user to switch between different configuration profiles (e.g., "Work" vs. "Personal") which contain distinct authentication tokens and histories.
*   **REQ-F-02 (Project Awareness):** The system must grant the Gemini Agent read/write access to the host's current working directory to perform code analysis and modifications.
*   **REQ-F-03 (Agent Tooling):** The runtime environment must provide a standard, rich suite of Linux command-line utilities. The Agent assumes the presence of standard GNU tools (`ls`, `grep`, `find`, `awk`, `sed`, `ps`) to explore and manipulate the codebase.
*   **REQ-F-04 (Authentication):** The system must support the CLI's OAuth web-flow, allowing the user to authenticate via a browser on the host machine.
*   **REQ-F-05 (Extension Support):** The system must support installing and running Gemini CLI extensions. Installed extensions (in `~/.gemini`) must persist. Local development extensions must be mountable via runtime arguments.
*   **REQ-F-06 (Sandboxing & Containment):** The primary architectural goal is to contain the Gemini CLI agent. It must be restricted to modifying files *only* within the explicitly mounted project directory and its own configuration files. It must **not** have write access to the host's OS system files, user home directory (outside of config), or other projects, preventing accidental corruption or deletion of sensitive external data.

### 2.2. Non-Functional Requirements
*   **REQ-N-01 (Interactive Latency):** The interactive chat interface must not exhibit perceptible input lag. Keystrokes must be echoed immediately.
*   **REQ-N-02 (Security - File Ownership):** Files created by the Agent on the host filesystem must be owned by the host user (UID/GID), never by `root`.
*   **REQ-N-03 (Transparency):** The wrapper script must pass through arbitrary arguments to the underlying CLI tool.
*   **REQ-N-04 (Portability):** The solution should run on standard Linux distributions with Docker installed.

### 2.3. System Constraints
*   **CON-01 (Toolchain):** Alpine Linux (BusyBox) is **prohibited** if its reduced toolset conflicts with the Agent's expected GNU flags (e.g., `grep -P`, `find -exec`).
*   **CON-02 (Filesystem Performance):** The solution must account for the I/O overhead of Docker Bind Mounts. Configurations that cause synchronous locking on the host volume (resulting in freezing/lag) are unacceptable.
