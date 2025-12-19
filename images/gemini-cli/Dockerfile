# Use official Node.js Slim image (Debian Bookworm based)
# Size: ~200MB base. Contains GNU coreutils (ls, grep, cat).
FROM node:20-bookworm-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# 1. Remove default 'node' user to free up UID 1000
RUN userdel -r node

# 2. Install essential tools and gosu
# gosu: for user switching
# git: for agent usage
# procps: provides 'ps' (useful for agent)
# findutils: provides standard GNU 'find'
RUN apt-get update && apt-get install -y --no-install-recommends \
    gosu \
    git \
    ca-certificates \
    procps \
    findutils \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Gemini CLI
# Clean cache to save space
RUN npm install -g @google/gemini-cli \
    && npm cache clean --force

# 4. Copy Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 5. Set Workdir
WORKDIR /home/gemini/workspace

# 6. Entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh", "gemini"]