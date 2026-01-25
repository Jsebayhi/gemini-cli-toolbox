# Hub Launcher: Implementation Plan

This plan details the steps to transform the Gemini Hub from a read-only dashboard into an active session launcher.

## Phase 1: Docker Socket Integration (Infrastructure)
*Goal: Enable the Hub container to control the host's Docker daemon.*

1.  **Host Script (`bin/gemini-toolbox`):**
    *   Update the Hub launch logic to include `-v /var/run/docker.sock:/var/run/docker.sock`.
    *   Detect and pass the host's Docker GID if necessary.
2.  **Hub Environment (`images/gemini-hub/Dockerfile`):**
    *   Install the `docker-ce-cli` (Docker binary) to allow executing `docker` commands.
3.  **Hub Runtime:**
    *   Verify the Hub can successfully execute `docker ps` from within the container.

## Phase 2: Workspace Mirroring (Path Logic)
*Goal: Align the Hub's filesystem with the Host's project directories.*

1.  **Toolbox Configuration:**
    *   Add a `--workspace <path>` flag to the toolbox script.
    *   Mirror-mount the workspace: `-v <HOST_PATH>:<HOST_PATH>`.
    *   Pass the path via `HOST_WORKSPACE_ROOT` environment variable.
2.  **Hub API (`app.py`):**
    *   Implement `/api/files` endpoint to browse directories starting from `HOST_WORKSPACE_ROOT`.
    *   Implement security guards to prevent traversal outside the root.

## Phase 3: Backend Launcher Logic (Script Reuse)
*Goal: Use the existing `gemini-toolbox` script to launch sessions, ensuring 100% consistency.*

1.  **Environment Prep:**
    *   Mount the `bin/gemini-toolbox` script into the Hub container (e.g., at `/usr/local/bin/gemini-toolbox`).
    *   Set `HOME` environment variable in the Hub to match the Host's `HOME` (passed via start args).
    *   Ensure `git` and `bash` are available in the Hub image.
2.  **Launch Execution:**
    *   Instead of constructing `docker run` manually, the Python app calls:
        ```python
        subprocess.run(
            ["gemini-toolbox", "--remote", AUTH_KEY], 
            cwd=target_project_path,
            env={...os.environ, "HOME": host_home_path}
        )
        ```
    *   This relies on DooD and Path Mirroring to work seamlessly.
3.  **API Endpoint:**
    *   Create `/api/launch` (POST) to trigger the script wrapper.

## Phase 4: Frontend UI (The Browser)
*Goal: Create a touch-friendly mobile file browser.*

1.  **Dashboard Update:**
    *   Add a "Start New Session" button.
2.  **Selection Flow:**
    *   Create a drill-down directory browser.
    *   "Launch Session" button for each directory.
3.  **Interaction:**
    *   Show loading state during container spawn.
    *   Redirect or refresh on success.

## Phase 5: Verification
1.  **Volume Check:** Ensure the launched session has the correct host files mounted.
2.  **Connectivity Check:** Verify the launched session joins the Tailscale mesh.
3.  **Cleanup:** Ensure `docker run --rm` is used so sessions clean up on exit.
