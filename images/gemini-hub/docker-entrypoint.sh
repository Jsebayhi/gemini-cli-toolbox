#!/bin/sh
set -e

# 1. Start Tailscale Daemon (Userspace Networking)
# --tun=userspace-networking: Avoids needing /dev/net/tun device (sometimes)
# --statedir: Mapped to named volume (/var/lib/tailscale) to persist Device ID
echo ">> Starting Tailscaled..."
tailscaled --tun=userspace-networking --statedir=/var/lib/tailscale &
sleep 3

# 2. Authenticate
if [ -z "$TAILSCALE_AUTH_KEY" ]; then
    echo "Error: TAILSCALE_AUTH_KEY is missing."
    exit 1
fi

echo ">> Authenticating with Tailscale..."
# Fixed hostname for consistent DNS (http://gemini-hub:8888)
# --force-reauth: Aggressively reclaim the 'gemini-hub' name if state was lost
HOSTNAME="gemini-hub"
tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname="$HOSTNAME" --force-reauth

echo ">> Gemini Hub Online: http://$HOSTNAME:8888"

# 3. Start Flask App
exec python run.py
