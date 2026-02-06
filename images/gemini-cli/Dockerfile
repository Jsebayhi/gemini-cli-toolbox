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
    npm install -g --verbose @google/gemini-cli \
    && cd $(npm root -g)/@google/gemini-cli \
    && npm install --package-lock-only \
    && (npm audit fix --only=prod || true) \
    && npm cache clean --force

# Patch IDE Host Detection
# The CLI forces 'host.docker.internal' in Docker, but the VS Code extension
# only accepts '127.0.0.1'. We patch it to respect GEMINI_CLI_IDE_SERVER_HOST.
RUN CORE_DIR=$(npm root -g)/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/ide \
    && TARGET_FILE="" \
    && if [ -f "$CORE_DIR/ide-connection-utils.js" ]; then TARGET_FILE="$CORE_DIR/ide-connection-utils.js"; \
       elif [ -f "$CORE_DIR/ide-client.js" ]; then TARGET_FILE="$CORE_DIR/ide-client.js"; fi \
    && if [ -n "$TARGET_FILE" ] && grep -q "export function getIdeServerHost() {" "$TARGET_FILE"; then \
        echo "Applying function-level patch for new CLI version to $TARGET_FILE..."; \
        sed -i "s/export function getIdeServerHost() {/export function getIdeServerHost() { if (process.env.GEMINI_CLI_IDE_SERVER_HOST) return process.env.GEMINI_CLI_IDE_SERVER_HOST;/" "$TARGET_FILE"; \
    elif [ -n "$TARGET_FILE" ] && grep -q "return isInContainer ? 'host.docker.internal' : '127.0.0.1'" "$TARGET_FILE"; then \
        echo "Applying line-level patch for legacy CLI version to $TARGET_FILE..."; \
        sed -i "s/return isInContainer ? 'host.docker.internal' : '127.0.0.1'/return process.env.GEMINI_CLI_IDE_SERVER_HOST || (isInContainer ? 'host.docker.internal' : '127.0.0.1')/" "$TARGET_FILE"; \
    else \
        echo "Error: Failed to find IDE host detection logic in $CORE_DIR. Upstream code may have changed." && exit 1; \
    fi

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