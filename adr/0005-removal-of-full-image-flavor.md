# ADR 0005: Removal of monolithic "Full" image variant

## Status
Accepted

## Context
Originally, the project provided a `gemini-cli-full` image (flagged via `--full`) that included multiple pre-installed language runtimes (Java, Go, Scala, Python, etc.). This was intended to give the AI agent an immediate environment for executing code.

However, this approach presented several challenges:
1.  **Maintenance Burden:** Each runtime required manual updates and version management within the Dockerfile.
2.  **Image Size:** The resulting image was extremely large (~2GB), making it slow to pull and store.
3.  **Version Inflexibility:** A single image could not feasibly contain all possible versions of every language a developer might need.

## Decision
We have decided to remove the `gemini-cli-full` image and the associated `--full` flag from the `gemini-toolbox` wrapper.

## Rationale
The introduction of **Docker-out-of-Docker (DooD)** integration (see ADR-0009 in `images/gemini-cli/adr/`) provides a superior alternative:
1.  **Orchestration vs. Inclusion:** Instead of *containing* every tool, the Gemini CLI now acts as an *orchestrator*. It can use the host's Docker daemon to launch small, official, and version-specific containers (e.g., `maven:3.9`, `python:3.11`, `golang:1.21`) for specific tasks.
2.  **Shared Cache:** Since it uses the host daemon, it benefits from the host's image cache, saving bandwidth and disk space.
3.  **Correctness:** The agent can choose the exact runtime version required by the project being analyzed, rather than being limited to what was pre-baked into the `:full` image.

## Consequences
*   **Positive:** Significant reduction in repository complexity and maintenance surface.
*   **Positive:** Faster image pulls and reduced disk usage for the primary toolbox.
*   **Negative:** The AI agent must now be prompted (or have the capability) to use `docker run` commands for code execution tasks, rather than assuming tools are locally available. This is mitigated by the toolbox's default DooD configuration.
