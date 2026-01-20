# Engineering Log

## 2025-12-19: Architecture Refactoring & Security Hardening

### 1. Permission Architecture (The "Gosu" Pivot)
**Problem:** Initial attempts to run as a non-root user (`--user $(id -u)`) caused write permission errors in `/home` inside the container, leading to immediate crashes or freezes of the Node.js application.
**Failed Solution:** `chmod 777 /home/gemini` (Insecure, brittle).
**Final Solution:** Adopted the "Entrypoint Fix" pattern using `gosu`.
*   Container starts as `root`.
*   Entrypoint creates a dynamic user matching host's `UID/GID`.
*   Entrypoint fixes ownership of `/home/gemini`.
*   Entrypoint drops privileges to the user via `gosu` before executing the app.

### 2. Monorepo Structure
**Problem:** The root directory was cluttered with build artifacts.
**Solution:** Adopted a `images/<tool>` structure.
*   `images/gemini-base`: System layer (Debian + Security Updates).
*   `images/gemini-stack`: SDK layer (Java, Go, Maven).
*   `images/gemini-cli`: App layer (Node.js + Gemini).
*   `Makefile`: Root orchestrator manages the build dependency graph.

### 3. Build Optimization (3-Tier Build)
**Problem:** `apt-get upgrade` is slow and bandwidth-intensive on every rebuild.
**Solution:** Split the build into tiers.
*   **Tier 1 (Base):** OS + Security patches. Built weekly.
*   **Tier 2 (Stack):** Heavy compilers (Java 8/17/21, Go, Maven). Built monthly.
*   **Tier 3 (App):** `npm install gemini-cli`. Built daily.
This ensures instant rebuilds for app changes while maintaining security.

### 4. Extensions & Caches
**Problem:** Downloads were not persisting, and extensions were hard to manage.
**Solution:**
*   **Caches:** Wrapper mounts host caches (`~/.m2`, `~/.sbt`, `~/.gradle`, `~/go`) directly into the container.
*   **Extensions:** Created a dedicated `/home/gemini/gemini_local_extensions` mount point.

### 5. CI/CD Security
**Problem:** Needed to ensure the image is free of vulnerabilities without paying for a registry.
**Solution:**
*   Implemented a local GitLab CI pipeline using `docker save` -> `tar`.
*   Added `aquasec/trivy` to scan the tarball.
*   Configured to fail on ANY fixable vulnerability.
