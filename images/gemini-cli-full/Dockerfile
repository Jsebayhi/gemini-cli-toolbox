# Tier 3: The Full Application
# Combines the heavy SDKs (Stack) with the latest Gemini CLI.

FROM gemini-cli-toolbox/stack:latest

# 1. Install Gemini CLI
# We accept the same build arguments if needed, but usually latest is fine
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
RUN TARGET_FILE=$(npm root -g)/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/ide/ide-client.js \
    && grep -q "return isInContainer ? 'host.docker.internal' : '127.0.0.1'" "$TARGET_FILE" \
    || (echo "Error: Failed to find IDE host detection logic in $TARGET_FILE. Upstream code may have changed." && exit 1) \
    && sed -i "s/return isInContainer ? 'host.docker.internal' : '127.0.0.1'/return process.env.GEMINI_CLI_IDE_SERVER_HOST || (isInContainer ? 'host.docker.internal' : '127.0.0.1')/" "$TARGET_FILE"

# 2. Copy Entrypoint (Reuse the robust one we wrote)
# We assume the build context includes the entrypoint from the sibling folder
# OR we can just create a new one. To keep it DRY, we should copy it.
# For now, I will write a simple Makefile to copy the entrypoint before build.
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 3. Setup Extensions
RUN mkdir -p /home/gemini/gemini_local_extensions

# 4. Set Workdir
WORKDIR /home/gemini/workspace

# 5. Entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh", "gemini"]

