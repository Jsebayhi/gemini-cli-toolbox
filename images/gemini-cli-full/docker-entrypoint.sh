#!/bin/sh
set -eu

UID=${DEFAULT_UID:-1000}
GID=${DEFAULT_GID:-1000}
USER=${DEFAULT_USERNAME:-gemini}
HOME=${DEFAULT_HOME_DIR:-/home/$USER}
DEBUG=${DEBUG:-false}

# Setup logging file descriptors
# FD 3 -> Debug Stdout
# FD 4 -> Debug Stderr
if [ "$DEBUG" = "true" ]; then
    exec 3>&1
    exec 4>&2
else
    exec 3>/dev/null
    exec 4>/dev/null
fi

# Create Group if missing
if ! getent group "$GID" >/dev/null 2>&1; then
    groupadd -g "$GID" "$USER" >&3 2>&4
fi

# Create User if missing
if ! getent passwd "$UID" >/dev/null 2>&1; then
    useradd -u "$UID" -g "$GID" -m -d "$HOME" -s /bin/bash "$USER" >&3 2>&4
fi

# Fix permissions
mkdir -p "$HOME"
chown -R "$UID:$GID" "$HOME"

# --- Remote Access (Tailscale) ---
if [ -n "${TAILSCALE_AUTH_KEY:-}" ]; then
    echo ">> Initializing Remote Access Mode (Tailscale)..."
    # Start tailscaled in the background
    # --tun=userspace-networking: works without /dev/net/tun if necessary
    # --statedir: store state in /tmp to avoid permission issues
    tailscaled --tun=userspace-networking --statedir=/tmp/tailscale &
    
    # Wait for daemon to be ready
    sleep 2
    
    # Generate meaningful hostname from project directory
    # 1. Get basename of workspace (current dir)
    # 2. Lowercase
    # 3. Replace non-alphanumeric with hyphens
    # 4. Limit length to avoid errors
    PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9' '-')
    
    # 5. Append unique suffix (first 4 chars of container hostname/id) to handle multiple instances
    UNIQUE_SUFFIX=$(hostname | cut -c1-4)
    TS_HOSTNAME="gemini-${PROJECT_NAME}-${UNIQUE_SUFFIX}"
    
    # Authenticate and bring up the node
    # Removed --ephemeral as it caused issues
    tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname="${TS_HOSTNAME}"
    echo ">> Remote Access Active. Hostname: ${TS_HOSTNAME}"
    echo ">> Find your IP in the Tailscale dashboard."
    
    # --- Session Mirroring (Tmux) ---
    echo ">> Starting Shared Session (Tmux)..."
    
    # Configure Tmux for better UX (Mouse Scrolling + History)
    # aggressive-resize is crucial for mobile + desktop sharing
    cat <<EOT > "$HOME/.tmux.conf"
set -g mouse on
set -g history-limit 50000
set -g default-terminal "screen-256color"
setw -g aggressive-resize on
EOT
    chown "$UID:$GID" "$HOME/.tmux.conf"
    
    # 1. Create a DETACHED tmux session named 'gemini' running the user's command
    # We must run this as the user so they own the session socket
    gosu "$UID:$GID" tmux new-session -d -s gemini "$@"
    
    # 2. Start Web Terminal (ttyd) in BACKGROUND
    # It attaches to the 'gemini' session
    # -p 3000: Port
    # -W: Writable
    ttyd -p 3000 -W gosu "$UID:$GID" tmux attach -t gemini > /tmp/ttyd.log 2>&1 &
    
    echo ">> Web Terminal active at http://<IP>:3000"
    echo ">> Attaching local session..."
    
    # 3. Attach the Foreground (Desktop) to the same session
    # We DO NOT use 'exec' here so we can catch the exit and clean up
    gosu "$UID:$GID" tmux attach -t gemini
    
    # Cleanup on exit
    echo ">> Session ended. Stopping remote services..."
    pkill tailscaled || true
    pkill ttyd || true
    exit 0
fi

# Export HOME so the child process uses the correct directory
export HOME

# Execute (Standard Mode)
exec gosu "$UID:$GID" "$@"
