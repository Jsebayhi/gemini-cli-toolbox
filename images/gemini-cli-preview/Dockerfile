# Use our custom secure base image
FROM gemini-base:latest

# 1. Install Gemini CLI
# Clean cache to save space
# 1. Install Gemini CLI
# Clean cache to save space
# Added --verbose to debug slow install
# Added --mount=type=cache to speed up rebuilds (persists ~/.npm)
# Added id=gemini-npm-cache to allow surgical pruning
RUN --mount=type=cache,target=/root/.npm,id=gemini-npm-cache \
    npm install -g --verbose @google/gemini-cli@preview \
    && cd $(npm root -g)/@google/gemini-cli \
    && npm install --package-lock-only \
    && (npm audit fix --only=prod || true) \
    && npm cache clean --force

# 4. Copy Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 5. Create Extensions Directory
# This folder is intended for mounting local extensions via Docker volumes
RUN mkdir -p /home/gemini/gemini_local_extensions

# 6. Set Workdir
WORKDIR /home/gemini/workspace

# 7. Entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh", "gemini"]