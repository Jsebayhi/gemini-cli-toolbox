# ADR-0049: Removal of Automatic Language Cache Mounting

## Status
Accepted

## Context
Since its inception, the Gemini CLI toolbox has automatically mounted several standard programming language cache directories from the host machine into the container. These include:
- `~/.m2` (Maven)
- `~/.gradle` (Gradle)
- `~/.sbt` (SBT)
- `~/.ivy2` (Ivy)
- `~/.cache/coursier` (Scala/Coursier)
- `~/go/pkg/mod` (Go Modules)
- `~/.cache/go-build` (Go Build Cache)

The goal was to provide a "zero-config" experience where builds are fast from the first run. However, this approach has several drawbacks:
1. **Implicit Side Effects:** It pollutes the user's host machine with artifacts generated inside the container.
2. **Security/Sandboxing:** It breaks the "sandbox" promise of the container by default.
3. **Complexity:** The wrapper script needs logic to pre-create these directories to avoid Docker creating them as `root`.
4. **Environment Discrepancies:** In environments like the Gemini Hub, these host paths might not exist or might be mapped differently, leading to startup errors or unexpected behavior.
5. **Redundancy:** With the introduction of **Configuration Profiles** (ADR-0021), users now have a first-class mechanism to define their own volume mounts and environment variables in a persistent, portable way.

## Decision
We will remove the automatic mounting of these language cache directories from the `gemini-toolbox` wrapper script. 

1.  **Remove Automounts:** The hardcoded `--volume` arguments for language caches will be removed from `bin/gemini-toolbox`.
2.  **Remove Pre-creation Logic:** The logic that ensures these directories exist on the host before launching Docker will be removed.
3.  **Documentation Update:** We will update the documentation to explain that sessions are now fully sandboxed by default and provide instructions on how to re-enable caching using profiles.

## Alternatives Considered

### 1. Maintain Status Quo (Automatic Mounting)
*   **Pros:** Zero-config build speed for first-time users.
*   **Cons:** Causes "Permission Denied" errors in non-root environments (like the Hub), pollutes the host filesystem with root-owned directories, and violates the "Sandbox" principle.
*   **Rejection Reason:** The operational cost in the Hub and the security implications outweigh the initial build speed convenience.

### 2. Introduce Explicit Language-Specific Flags (e.g., `--cache-java`)
*   **Pros:** Explicit control without requiring profile configuration.
*   **Cons:** Leads to "flag bloat" in the wrapper script. Adding a flag for every possible language (Python, Node, Java, Go, Rust, etc.) is not scalable.
*   **Rejection Reason:** Configuration Profiles are a more generic and powerful mechanism that solves this problem for all languages without adding specific flags to the CLI.

### 3. Interactive Prompt on First Run
*   **Pros:** Educational; asks the user for permission before mounting.
*   **Cons:** Breaks non-interactive/automated workflows and creates a jarring user experience for a CLI tool meant for speed.
*   **Rejection Reason:** Directives from the Hub or automated scripts must remain seamless and non-blocking.

## Consequences
- **Improved Isolation:** Sessions are now more secure and isolated from the host by default.
- **Simplified Codebase:** The `bin/gemini-toolbox` script is cleaner and easier to maintain.
- **Explicit Configuration:** Users must now explicitly choose to share their host caches, adhering to the principle of least privilege.
- **Breaking Change for Performance:** Users might notice slower first-time builds in new sessions if they don't configure their profiles to include caches.
