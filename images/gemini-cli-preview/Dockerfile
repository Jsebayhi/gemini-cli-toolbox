# Use our custom secure base image
FROM gemini-cli-toolbox/base:latest

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

# Patch IDE Host Detection
RUN TARGET_FILE=$(npm root -g)/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/ide/ide-client.js \
    && grep -q "return isInContainer ? 'host.docker.internal' : '127.0.0.1'" "$TARGET_FILE" \
    || (echo "Error: Failed to find IDE host detection logic in $TARGET_FILE. Upstream code may have changed." && exit 1) \
    && sed -i "s/return isInContainer ? 'host.docker.internal' : '127.0.0.1'/return process.env.GEMINI_CLI_IDE_SERVER_HOST || (isInContainer ? 'host.docker.internal' : '127.0.0.1')/" "$TARGET_FILE"

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