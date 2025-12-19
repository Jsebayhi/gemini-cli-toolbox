# Engineering Log: Containerizing Gemini CLI

This document chronicles the iterative engineering process to create a working Dockerized environment for the interactive `@google/gemini-cli`.

## The Goal
To run the interactive `gemini` CLI in a Docker container with:
1.  **Identity Isolation:** Separate configuration/auth profiles.
2.  **Project Context:** Access to working directory.
3.  **Permissions:** Files owned by the host user.

## The Journey (Failure Modes & Fixes)

### 1. Permissions & Crashes
**Issue:** Running as default user caused permission errors in `/home`.
**Fix:** Adopted the **Entrypoint Pattern** (`gosu`) to create a user matching the Host UID at runtime.

### 2. The "Input Lag" & The Config Folder Discovery
**Symptom:** Severe input lag (keys dropped, freezing) when typing.
**Initial Hypothesis:** Alpine Linux (`musl` libc) was incompatible with Node TTY.
**Action:** Switched to Debian (`bookworm`). Lag persisted.
**Discovery:** The user's `~/.gemini` configuration folder was **800MB**.
**Analysis:** The application performs synchronous file I/O on the configuration directory (likely history/logs) during the input loop. Mounting this 800MB folder via Docker Bind Mount caused the main thread to block.
**Resolution:**
1.  **Root Cause:** Massive config folder.
2.  **Fix:** User cleaned the folder.
3.  **Architecture:** We retained **Debian (`bookworm-slim`)** as the base image. While Alpine *might* work with a clean config, Debian provides the standard `glibc` environment, native `gosu` package, and maximum compatibility for Node.js tools, making it the superior choice for a robust toolbox.

## Final Architecture

### 1. Dockerfile
```dockerfile
# Debian Bookworm (Stable) for glibc compatibility
FROM debian:bookworm-slim
# gosu for secure user switching
RUN apt-get install gosu ...
# Clean user space (no pre-existing node user)
```

### 2. Wrapper Script
*   **Mounts:** Maps host config to container home.
*   **Networking:** Host networking for OAuth.
*   **Entrypoint:** Dynamic UID mapping.

## Key Lesson
**"Probe, Don't Assume."** The input lag appeared to be a low-level OS issue (Musl vs Glibc), but was actually an application-level I/O bottleneck caused by "Data Debt" (800MB log file).