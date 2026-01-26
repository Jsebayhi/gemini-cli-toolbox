# ADR 0006: Hub Lifecycle and Profile Discovery

## Status
Accepted

## Context
The Gemini Hub serves as a persistent entry point for mobile devices to discover and launch sessions. Two issues were identified with its initial behavior:

1.  **Aggressive Shutdown:** The Hub was configured to shut down automatically after 60 seconds of inactivity (no active CLI sessions). This proved too aggressive, as users often disconnect a session to switch profiles or take a break, only to find the Hub dead when they return.
2.  **Profile Isolation:** When launching a session with a specific profile (e.g., `~/.gemini-profiles/work`), the Hub didn't inherently know about other potential profiles in that same directory structure, limiting discovery.

## Decisions

### 1. Opt-in Auto-Shutdown
The auto-shutdown mechanism is now **disabled by default**.
*   **Rationale:** The Hub is a lightweight service. Keeping it running allows for a "Always On" discovery portal on the user's Tailnet, which is the primary value proposition.
*   **Mechanism:** The shutdown monitor thread checks for the environment variable `HUB_AUTO_SHUTDOWN=1`.
*   **CLI Support:** The `gemini-hub` script exposes an `--auto-shutdown` flag to enable this for specific use cases (e.g., temporary CI/CD environments).

### 2. Contextual Config Root
We leverage the user's intent when launching `gemini-toolbox` to configure the Hub's discovery scope.

*   **Scenario:** User runs `gemini-toolbox --profile ~/.gemini-profiles/work`.
*   **Inference:** The user is likely organizing profiles in `~/.gemini-profiles/`.
*   **Action:** The toolbox calculates the parent directory (`~/.gemini-profiles/`) and passes it to the Hub as the `--config-root`.
*   **Result:** The Hub UI automatically lists "work" alongside any sibling profiles (e.g., "personal", "client-a"), enabling seamless switching.

### 3. Workspace Mirroring
The toolbox continues to pass the current project directory as a `--workspace` to the Hub. This ensures that the specific project the user is working on is immediately available for browsing in the Hub wizard.

## Consequences
*   **Positive:** Improved UX. Users can exit a session and immediately launch a new one via the Hub without restarting the service.
*   **Positive:** Better discovery. The Hub becomes "aware" of the user's profile organization strategy.
*   **Negative:** The user must manually stop the Hub (`gemini-toolbox stop-hub`) if they want to free up the small amount of resources it consumes.
