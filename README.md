# Dockerized CLI Toolbox

A collection of containerized command-line tools designed for security, portability, and ease of use. Each tool is self-contained with its own build context and wrapper script.

## Available Tools

| Tool | Description | Documentation |
| :--- | :--- | :--- |
| **gemini-cli** | Wrapper for `@google/gemini-cli`. Features persistent auth, context mounting, and seamless TTY handling. | [Read Docs](images/gemini-cli/README.md) |

## Getting Started

### Prerequisites
- Docker
- Make
- Bash

### Global Build
To build all tools in the toolbox:
```bash
make build
```

To build a specific tool:
```bash
make -C images/gemini-cli build
```

### Installation
Symlink the wrapper scripts to your path:

```bash
# Gemini CLI
ln -s $(pwd)/bin/gemini-docker ~/.local/bin/gemini-docker
```

## Repository Structure

```text
.
├── Makefile                # Master Orchestrator
├── bin/                    # Wrapper Scripts (User Interface)
│   └── gemini-docker
└── images/                 # Tool Definitions
    └── gemini-cli/
        ├── Dockerfile
        ├── Makefile
        ├── README.md
        └── ...
```
