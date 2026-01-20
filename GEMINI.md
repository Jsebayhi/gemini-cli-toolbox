# Project Context: Dockerized CLI Toolbox

This document provides high-level operational context for AI agents working on the repository as a whole.

## 1. Project Overview
A modular "Toolbox" repository containing multiple self-contained Dockerized CLI tools. Each tool resides in `images/<tool-name>` and manages its own lifecycle.

## 2. Repository Structure

| Directory | Purpose |
| :--- | :--- |
| `bin/` | **User Interface.** Wrapper scripts that users invoke directly. |
| `images/` | **Components.** Source code for each Docker image. |
| `images/gemini-cli/` | **Gemini CLI.** [See Component Context](images/gemini-cli/GEMINI.md) |
| `Makefile` | **Orchestrator.** Master makefile for global build tasks. |

## 3. Global Workflows

### Adding a New Tool
1. Create `images/<new-tool>/`.
2. Add `Dockerfile`, `Makefile`, and `GEMINI.md` specific to that tool.
3. Add a wrapper script in `bin/`.
4. Register the tool in the root `README.md`.

### Global Build
```bash
make build
```

## 4. Core Mandates

### Documentation is Code
*   **Mandate:** You must strictly maintain all documentation (`README.md`, `GEMINI.md`, `adr/*`) in sync with code changes.
*   **Trigger:** Any time you rename files, change architecture, modify workflows, or discover new gotchas, you **MUST** update the corresponding documentation in the same turn.
*   **User-Facing Rule:** If you add a new feature (e.g., a flag, a command, a capability) or change behavior, you **MUST** update the root `README.md` to reflect this immediately. Do not leave features undocumented.
*   **Why:** This project relies on the "Golden Artifact" pattern where the documentation is the source of truth for future sessions.

### Context Management
*   **Rule:** When working on a specific tool, **load its specific `GEMINI.md`**.
*   **Why:** The root context is generic; the component context contains the critical "gotchas" for that specific image.