# 32. Always-on Multiplexing

Date: 2026-02-12

## Status

Accepted

## Context

Originally, the Gemini CLI Toolbox architecture distinguished between "Local" and "Remote" sessions. 
- **Remote Sessions:** Initialized a `tmux` session to support the web-based terminal (`ttyd`).
- **Local Sessions:** Executed the Gemini CLI process directly as the container's PID 1 (via `exec gosu`).

This distinction created a significant resilience gap. If the user's terminal emulator or IDE (e.g., VS Code) crashed while running a Local Session, the container and process would remain alive, but the user effectively lost access to the interactive session.
- `docker attach` is unreliable for Node.js processes that are not TTY-aware, often blocking input.
- `gemini-toolbox connect` failed because it expected a `tmux` socket that didn't exist.

## Decision

We will standardize session management by wrapping **all** Gemini CLI sessions inside a `tmux` session by default, regardless of the connection mode (Local or Remote).

### 1. Entrypoint Refactor
The `docker-entrypoint.sh` will be modified to:
- Always create a detached `tmux` session named `gemini` for the primary command.
- Automatically attach to this session in the foreground.
- This effectively makes the `tmux` layer invisible to the user during normal operation but ensures a persistent socket exists.

### 2. Opt-out Mechanism
We recognize that some advanced use cases (e.g., automated debugging, CI/CD wrappers) may require the raw PID 1 process.
- We support a `GEMINI_TOOLBOX_TMUX=false` environment variable.
- We add a `--no-tmux` flag to the `gemini-toolbox` CLI to trigger this setting.
- When this flag is used, the legacy behavior (direct `exec`) is restored.

### 3. Connection Logic
The `gemini-toolbox connect` command will be updated to:
- Prioritize `tmux attach -t gemini` as the standard reconnection method.
- Fail explicitly with a clear error message if no `tmux` session is found (i.e., if the user opted out), rather than attempting to fallback to a disconnected `bash` shell or a broken `docker attach`.

## Consequences

### Positive
- **Resilience:** Users can recover any standard session after a terminal crash by running `gemini-toolbox connect`.
- **Consistency:** Local and Remote sessions now behave identically regarding process management.
- **Maintainability:** The entrypoint logic is simplified by removing the conditional branching for `tmux` setup.

### Negative
- **Complexity:** Adds a slight overhead (memory/CPU) of running `tmux` for every session.
- **Signal Handling:** `tmux` captures signals like `SIGINT`. While usually desired, it changes the behavior slightly compared to a raw process (e.g., `Ctrl+C` might be trapped by tmux config).

## Compliance
This decision aligns with the core mandate of providing a robust and safe developer experience.
