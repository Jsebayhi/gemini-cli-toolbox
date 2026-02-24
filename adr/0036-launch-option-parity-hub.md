# ADR-0036: Launch Option Parity in Gemini Hub

## Status
Proposed

## Context
The Gemini Hub Web UI currently supports a subset of the configuration options available in the `gemini-toolbox` CLI. While some options like `image_variant` (preview), `docker_enabled`, `ide_enabled`, and `worktree_mode` have been partially implemented in the `issue-15` branch, users still lack control over other critical flags such as overriding the Docker image (`--image`) and passing custom Docker arguments (`--docker-args`).

Note: Some CLI flags like `--no-tmux` are intentionally excluded from the Hub UI because they are incompatible with the `--remote` mode required for the Hub's web terminal access.

## Decision
We will enhance the Gemini Hub launch wizard and backend to support the relevant CLI options, completing the partial implementation.

### 1. Backend Enhancements
The `LauncherService` in the `gemini-hub` component will be updated to accept and process the following additional parameters:
- `custom_image`: Allows overriding the default Docker image (maps to `--image`).
- `docker_args`: Allows passing raw arguments to `docker run` (maps to `--docker-args`).

### 2. Frontend Enhancements (UI/UX)
To maintain a clean user interface while providing advanced control, we will introduce an **"Advanced Options"** section in the launch wizard. This section will be collapsed by default.

#### UI Components:
- **Toggle/Collapse**: An "Advanced Options" chevron or button to reveal/hide the additional settings.
- **Gemini CLI Variant Selection**: A dropdown to choose between:
    - **Stable**: Standard image (Default).
    - **Preview**: Beta image (`--preview`).
    - **Custom**: Reveals a text input to specify a custom Docker image name (`--image`).
- **Additional Docker Args Input**: A text area for specifying raw arguments like `-v /host:/container`.

### 3. Argument Mapping Logic
The Hub will continue to follow the CLI's logic for argument precedence:
1.  Profile `extra-args` are applied first.
2.  UI-selected options are applied next, overriding profile defaults where applicable.
3.  For additive arguments like `--docker-args`, the Hub will ensure both profile and UI arguments are passed.

## Alternatives Considered

### Alternative 1: Flat UI (Always Visible)
- **Pros**: All options are immediately discoverable.
- **Cons**: Overwhelms casual users with complexity. Conflicts with the "simple and clean" aesthetic of the Hub.
- **Rejection**: Rejected in favor of progressive disclosure.

### Alternative 2: JSON Configuration Block
- **Pros**: Extremely flexible; can support any future flag without UI changes.
- **Cons**: Poor UX for non-technical users. Error-prone.
- **Rejection**: Rejected as it defeats the purpose of a user-friendly Web UI.

### Alternative 3: Profile-Only Configuration
- **Pros**: No UI changes needed.
- **Cons**: Requires users to modify files on disk to change a single launch parameter, which is counter-intuitive for a web-based management tool.
- **Rejection**: Rejected as it doesn't achieve the goal of "parity" with the CLI's on-the-fly capabilities.

## Consequences
- **Positive**: Users gain full control over their sessions from the web interface.
- **Positive**: Reduced need to switch back to the CLI for specialized tasks.
- **Negative**: Increased complexity in the launch wizard code (both JS and Python).
- **Negative**: Potential for users to break their sessions by providing invalid `docker-args` (mitigated by displaying the launch log/error).
