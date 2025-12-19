# Understanding `gosu`: The Key to Docker Permissions

This document explains the role of `gosu` in our Docker architecture and why it is the "secret sauce" for interactive containerized applications.

## The Challenge
To run the Gemini CLI effectively, we have two conflicting requirements:
1.  **Start as Root:** We need Root privileges at startup to dynamically create a user that matches your host's UID/GID (so you own the files the container writes).
2.  **Run as User:** We must execute the actual application as that standard user, not Root.

## The Failed Alternatives

### 1. `docker run --user` (Host-Side)
*   **Method:** Tell Docker to start as a specific UID directly.
*   **Problem:** The container starts as a "nobody" user. It cannot fix permissions on `/home` or install runtime dependencies because it never had Root access. This leads to the "Permission Denied" crashes.

### 2. Standard `su` (Switch User)
*   **Method:** Start as Root, then run `su -c "gemini" user`.
*   **Problem:** `su` runs the application as a **child process**.
    *   **Signals Break:** If you hit `Ctrl+C`, the signal hits `su`, but `su` often fails to pass it to the child. The app hangs.
    *   **TTY Issues:** `su` creates a new session layer, which often breaks the direct link between your keyboard and the Node.js readline interface (causing the "freeze").

## The Solution: `gosu`

`gosu` is a lightweight tool designed specifically for containers. It allows a Root process to step down to a normal user **without creating a child process**.

### How it Works
When our entrypoint script runs:
```bash
exec gosu user:group gemini "$@"
```

1.  **User Switch:** `gosu` switches the current process from Root to the specified `user:group`.
2.  **Process Replacement (`exec`):** It executes the `gemini` command by **replacing** the `gosu` process in memory.
    *   *Before:* PID 1 is `entrypoint.sh`.
    *   *After:* PID 1 is `gemini`.

### Why We Need It
*   **Direct Signal Handling:** Because `gemini` becomes PID 1, your keyboard inputs (text, Ctrl+C) go directly to the application. There is no middleman to buffer or block them.
*   **Clean Permissions:** The application runs purely as your user, ensuring all files written to your mounted volumes are owned by you, not Root.

In short, `gosu` gives us the **setup power of Root** with the **runtime safety of a User**, without breaking the interactive terminal.
