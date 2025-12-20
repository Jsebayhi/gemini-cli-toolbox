# Use our custom secure base image
FROM gemini-base:latest

# 1. Install Gemini CLI
# Clean cache to save space
# We runs 'npm audit fix' inside the package folder to patch sub-dependency CVEs
# Note: We must generate a package-lock.json first because global installs don't keep it
RUN npm install -g @google/gemini-cli \
    && cd $(npm root -g)/@google/gemini-cli \
    && npm install --package-lock-only \
    && npm audit fix --only=prod \
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