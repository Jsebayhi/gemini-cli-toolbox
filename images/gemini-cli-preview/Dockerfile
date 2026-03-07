# Use our custom secure base image
ARG BASE_IMAGE=gemini-cli-toolbox/base:latest
FROM ${BASE_IMAGE}

# 1. Configure Mount-Proof User-Space NPM Prefix
# We use /opt instead of /home/gemini to ensure the CLI isn't hidden 
# if a user mounts a volume to their home directory.
ENV NPM_CONFIG_PREFIX=/opt/npm-global
ENV PATH=$NPM_CONFIG_PREFIX/bin:$PATH

# 2. Install Gemini CLI
# Clean cache to save space
# Added --verbose to debug slow install
# Added --mount=type=cache to speed up rebuilds (persists ~/.npm)
# Added id=gemini-npm-cache to allow surgical pruning
RUN --mount=type=cache,target=/root/.npm,id=gemini-npm-cache \
    mkdir -p $NPM_CONFIG_PREFIX && \
    chmod 777 $NPM_CONFIG_PREFIX && \
    npm install -g --verbose --prefix $NPM_CONFIG_PREFIX @google/gemini-cli@preview && \
    chmod -R 777 $NPM_CONFIG_PREFIX

# Patch Gemini CLI (IDE Host Detection and Infinite Retry)
# We delegate to robust shared scripts that handle both bundled and multi-file structures.
COPY --from=scripts patch-ide.sh patch-retry.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/patch-*.sh && \
    /usr/local/bin/patch-ide.sh $NPM_CONFIG_PREFIX && \
    /usr/local/bin/patch-retry.sh $NPM_CONFIG_PREFIX

# 4. Copy Entrypoint
COPY --from=scripts docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 5. Create Extensions Directory
# This folder is intended for mounting local extensions via Docker volumes
RUN mkdir -p /home/gemini/gemini_local_extensions

# 6. Set Workdir
WORKDIR /home/gemini/workspace

# 7. Entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh", "gemini"]
