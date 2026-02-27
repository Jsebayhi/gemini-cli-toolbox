# ADR-0054: Infinite Retry for High Demand in Gemini CLI

## Status
Proposed

## Context
When the Gemini models are in high demand, the `@google/gemini-cli` defaults to showing a dialog box to the user after 3 retries. This behavior is disruptive for users who would prefer to "set it and forget it," especially during long-running tasks or automated sessions.

The user wants the CLI to keep retrying indefinitely and notify them only when the task is finally completed.

## Decision
We will patch the `@google/gemini-cli` inside the Docker image during the build process to automatically return a `retry_always` intent when a "high demand" error occurs.

### Alternatives Considered
1. **Upstream PR:** Ideally, this should be a configuration flag in the official CLI. However, this is slow and may not align with Google's UI preferences.
2. **Wrapper Script:** We could attempt to catch the error in a wrapper, but the CLI's internal state (e.g., chat history, tool executions) is hard to manage from the outside.
3. **Patching (Chosen):** Modifying the compiled JS in the Docker image is the most direct and reliable way to change this behavior for our users immediately.

## Implementation
We will use `sed` within the `images/gemini-cli/Dockerfile` to modify `dist/src/ui/hooks/useQuotaAndFallback.js`.

To ensure robustness:
1. We will use `grep` to verify the presence of the unique target string `message = messageLines.join('\n');` before applying the patch.
2. If `grep` fails (meaning the upstream code has changed), the build will exit with an error, alerting us to update the patch.
3. The patch will replace the target line with `return 'retry_always';`. This effectively skips the subsequent lines that set error flags and open the UI dialog, providing a seamless background retry.

**Rationale for Early Return:** 
We intentionally bypass the lines that set `quotaErrorOccurred` to `true`. In the original code, these flags are only reset when a user manually clicks "Retry". By skipping them during an automated retry, we prevent the CLI from entering a "sticky" error state (which would disable features like Next Speaker Check) and ensure that when the request finally succeeds, the system is in a clean, non-error state.

**Note on Backoff:**
 The `@google/gemini-cli-core` package implements an exponential backoff strategy with a hardcoded `maxDelayMs` of **30,000ms (30 seconds)**. This ensures that even with infinite retries, the delay between attempts will never exceed 30 seconds, maintaining a reasonable level of responsiveness.

## Consequences
- **Pros:** Seamless "infinite retry" experience for users during high demand. No more annoying dialog boxes.
- **Cons:** We are maintaining a manual patch on a third-party dependency.
- **Maintenance:** The build will fail if `@google/gemini-cli` changes its error handling logic significantly, requiring a manual update to the `sed` patterns.
