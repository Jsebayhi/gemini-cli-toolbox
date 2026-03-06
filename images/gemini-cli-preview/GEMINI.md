# Component Context: Gemini CLI (Preview)

This document provides operational context for AI agents working specifically on the `gemini-cli-preview` container.

## 1. Component Overview
A bleeding-edge version of the Gemini CLI image, installing `@google/gemini-cli@preview`. It follows the same architecture as the stable image but often experiences structural changes (e.g., bundling) earlier.

## 2. File Map (Component Level)

| File | Purpose |
| :--- | :--- |
| `Dockerfile` | **The Environment.** Node.js 20 (Bookworm) with the Preview CLI. |
| `ADR/` | Refer to stable image ADRs for architecture decisions. |

## 3. Operational Workflows

### Building (Local)
Run from project root:
```bash
make build-cli-preview
```

## 4. Known Peculiarities & Gotchas

### Upstream Packaging (Bundling)
As of early 2026, the `@preview` version shifted to a bundled package format (`bundle/gemini.js`). This significantly differs from the traditional `dist/src/` structure found in the stable version.

### Source Code Patching
*   **Discovery:** This image uses a robust, loop-based patching strategy that handles both bundled and legacy formats. It uses `patch-cli.sh` to discover and patch target files.
*   **Rules:** See the stable image `GEMINI.md` for the core patching mandates and rationale.

### Interactive vs. Automated
The Infinite Retry patch is particularly critical for this image as it's often used by other agents or automated pipelines to test new features.
