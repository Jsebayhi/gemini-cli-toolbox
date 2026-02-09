# Base Image for Gemini CLI Toolbox
# Contains: Python (Latest Stable), Node.js 20, OS Security Updates, Gosu, Git, GH CLI, GLAB CLI

# --- Stage 1: Source Node.js ---
# We harvest the Node.js binaries from the official image to ensure they are correct
FROM node:20-bookworm-slim AS node-source

# --- Stage 2: Final Image ---
# We use 'python:slim' which always points to the LATEST stable Python version on Debian
# This satisfies the requirement: "not have to update the dockerfile... when there will be a new release"
FROM python:slim

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Node.js (Grafted from Stage 1)
# We copy /usr/local which contains bin/node, lib/node_modules, and bin/npm symlinks
COPY --from=node-source /usr/local /usr/local

# 2. System Updates & Essentials
# - make: Added per request
# - gosu: for user switching
# - git, procps, findutils: Standard agent toolkit
# - xsel: for /copy command
# - tailscale: for remote access (Container-Encapsulated Mode)
# - ttyd: Web terminal (Static binary download)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    make \
    gosu \
    git \
    ca-certificates \
    procps \
    findutils \
    xsel \
    vim \
    bash-completion \
    locales \
    curl \
    wget \
    netcat-openbsd \
    gnupg \
    tmux \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y tailscale gh glab \
    && curl -fsSL -o /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 \
    && chmod +x /usr/local/bin/ttyd \
    && rm -rf /var/lib/apt/lists/* \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

# 2.1 Install Docker CLI (DooD Support)
# We install the CLI and Compose plugin to talk to the host's daemon via socket
RUN install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# 3. Configure Python for "Toolbox" Usage
# - Allow 'gemini' user (and others) to install packages globally
# - Disable the "externally managed environment" warning for pip
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PIP_ROOT_USER_ACTION=ignore

# Grant global write access to Python's install directories
# This allows 'pip install' to work immediately without sudo or --user
RUN chmod -R 777 /usr/local/lib/python* \
    && chmod 777 /usr/local/bin

# 4. Shell Configuration
# - Enable bash completion
# - Force bash to append history to disk after every command (history -a)
RUN echo "if [ -f /usr/share/bash-completion/bash_completion ]; then . /usr/share/bash-completion/bash_completion; fi" >> /etc/bash.bashrc && \
    echo 'export PROMPT_COMMAND="history -a"' >> /etc/bash.bashrc