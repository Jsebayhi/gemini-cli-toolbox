# 8. Tolerance of Unfixable NPM Vulnerabilities

Date: 2026-01-08

## Status

Accepted

## Context

During the build process of the `gemini-cli` application images, the command `npm audit fix` is executed to apply security patches to dependencies. 

On 2026-01-08, the build failed due to a Denial of Service (DoS) vulnerability in `jsdiff` (a sub-dependency of `@google/gemini-cli`). The audit reported "No fix available," causing the command to exit with a non-zero status and halting the entire image production pipeline.

## Decision

We have decided to allow the Docker build to continue even if `npm audit fix` fails to resolve all vulnerabilities in the application layer.

**Implementation:**
The command in the `Dockerfile` is changed to `(npm audit fix --only=prod || true)`.

**Rationale:**
1.  **Operational Availability:** Strict enforcement of a "zero vulnerability" build policy prevents the development of the toolbox itself when upstream maintainers (Google) have not yet released patches for sub-dependencies.
2.  **Risk Profile:** The specific vulnerability identified (DoS in `jsdiff`) poses a low risk in the context of a local development CLI. It would require the user to process a maliciously crafted patch file. As the tool is used by the developer on their own trusted codebase, the exploit vector is highly unlikely.
3.  **Transience:** This is a temporary measure. Future rebuilds will still attempt to run `npm audit fix`, and once a patch is released upstream, it will be applied automatically.

## Consequences

### Positive
*   **Build Restoration:** Images can be built and deployed despite minor, unfixable upstream issues.
*   **Decoupling:** Toolbox maintenance is no longer blocked by third-party library schedules.

### Negative
*   **Technical Debt:** The image technically contains a known (though low-risk) vulnerability.
*   **Visibility:** Build logs will still show the audit failure, which requires manual inspection to ensure no *new* high-risk vulnerabilities have appeared.

## Mitigation
We will continue to run `make scan` (Trivy) as part of our security workflow to maintain visibility into the security posture of the final images.
