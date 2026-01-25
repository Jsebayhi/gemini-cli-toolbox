FROM python:3.11-slim-bookworm

# 1. Install Dependencies
# - curl, gnupg: for tailscale repo
# - Flask: for the web server
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && pip install flask

# 2. Install Tailscale (Official Repo)
RUN mkdir -p --mode=0755 /usr/share/keyrings \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
    && apt-get update \
    && apt-get install -y tailscale \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy Application
WORKDIR /app
COPY app.py .
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 4. Runtime
EXPOSE 8888
ENV PORT=8888

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
