# Dockerized Gemini CLI

A lightweight, secure, and robust wrapper for running the `@google/gemini-cli` in Docker.

## Features
- **Zero Configuration:** Works out of the box with your native terminal.
- **Secure:** Runs as your host user (no permission issues).
- **Persistent:** Keeps configuration and auth in `~/.gemini` (or custom path).
- **Fast:** Optimized Debian-based image for lag-free input.

## Installation

1.  **Build the Image:**
    ```bash
    make build
    ```
    *(Run this from the project root)*

2.  **Install the Wrapper:**
    ```bash
    ln -s $(pwd)/../../bin/gemini-docker ~/.local/bin/gemini-docker
    ```

## Usage

**Interactive Session:**
```bash
gemini-docker
```

**One-Shot Query:**
```bash
gemini-docker "Explain how Docker entrypoints work"
```

**Using a Specific Model:**
```bash
gemini-docker --model gemini-1.5-pro "Write a poem"
```

**Custom Project Context:**
Mounts a specific directory as the workspace.
```bash
gemini-docker --project ~/my-code
```

**Custom Configuration (e.g., Work Profile):**
Uses a separate authentication/config folder.
```bash
gemini-docker --config ~/.gemini-work
```

**Local Extensions:**
To use a locally developed extension, mount it into the container using `--docker-args`.
```bash
gemini-docker --docker-args "-v /path/to/my-extension:/extensions" -- --extensions /extensions/my-extension
```

**Debug Mode (Shell):**
Drops you into a bash shell inside the container for troubleshooting.
```bash
gemini-docker --debug
```

## Architecture
- **Structure:** Self-contained build context.
- **Base:** `node:20-bookworm-slim` (Debian)
- **Entrypoint:** `gosu` for seamless user switching.
- **Network:** Host networking for OAuth callbacks.

For detailed design decisions, see the [Architecture Decision Records (ADR)](adr/).
For the technical specification, see [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md).
