#!/bin/sh
set -e

# 1. Start Tailscale Daemon (Userspace Networking)
# --tun=userspace-networking: Avoids needing /dev/net/tun device (sometimes)
# --statedir: Mapped to named volume (/var/lib/tailscale) to persist Device ID
echo ">> Starting Tailscaled..."
tailscaled --tun=userspace-networking --statedir=/var/lib/tailscale &
sleep 3

# 2. Authenticate
# Check if already authenticated (non-zero exit code means not authenticated)
if tailscale status >/dev/null 2>&1; then
    echo ">> Already authenticated with Tailscale."
else
    if [ -z "$TAILSCALE_AUTH_KEY" ]; then
        echo "Error: TAILSCALE_AUTH_KEY is missing and not already authenticated."
        exit 1
    fi

    echo ">> Authenticating with Tailscale..."
    # Fixed hostname for consistent DNS (http://gemini-hub:8888)
    HOSTNAME="gemini-hub"
    tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname="$HOSTNAME"
fi

echo ">> Gemini Hub Online: http://gemini-hub:8888"

# 3. Start Flask App
exec python run.py
