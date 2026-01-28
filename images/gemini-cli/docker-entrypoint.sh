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

# Identify the actual username for the UID (in case it pre-existed)
TARGET_USER=$(getent passwd "$UID" | cut -d: -f1)

# Fix permissions
mkdir -p "$HOME"
chown -R "$UID:$GID" "$HOME"

# --- Docker-out-of-Docker Setup ---
if [ -n "${HOST_DOCKER_GID:-}" ] && [ -S "/var/run/docker.sock" ]; then
    if [ "$DEBUG" = "true" ]; then
        echo ">> Setting up Docker Access (GID: $HOST_DOCKER_GID)..." >&3
    fi

    # Check if a group with this GID already exists
    if ! getent group "$HOST_DOCKER_GID" >/dev/null 2>&1; then
        groupadd -g "$HOST_DOCKER_GID" host-docker >&3 2>&4
    fi
    
    # Add user to the group
    usermod -aG "$HOST_DOCKER_GID" "$TARGET_USER" >&3 2>&4
fi

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
    if [ -n "${GEMINI_SESSION_ID:-}" ]; then
        # Preferred: Use the ID passed from the toolbox script (Guaranteed Consistency)
        # Format: gem-{PROJECT}-{TYPE}-{UUID}
        TS_HOSTNAME="${GEMINI_SESSION_ID}"
    else
        # Fallback: Legacy generation (for manual docker run usage)
        RAW_PROJ="${GEMINI_PROJECT_NAME:-$(basename "$(pwd)")}"
        RAW_TYPE="${GEMINI_SESSION_TYPE:-unknown}"
        
        CLEAN_PROJ=$(echo "$RAW_PROJ" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')
        CLEAN_TYPE=$(echo "$RAW_TYPE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')
        UNIQUE_SUFFIX=$(hostname | cut -c1-4)
        
        TS_HOSTNAME="gem-${CLEAN_PROJ}-${CLEAN_TYPE}-${UNIQUE_SUFFIX}"
    fi
    
    # Authenticate and bring up the node
    # Removed --ephemeral as it caused issues
    echo ">> Registering VPN Node: ${TS_HOSTNAME}"
    tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname="${TS_HOSTNAME}"
    echo ">> Remote Access Active."
    
    # --- Tmux Configuration ---
    # Enable mouse support to allow scrolling in ttyd/browser
    if [ ! -f "$HOME/.tmux.conf" ]; then
        if [ "$DEBUG" = "true" ]; then
            echo ">> Generating default .tmux.conf..." >&3
        fi
        {
            echo "set -g mouse on"
            echo "set -g history-limit 50000"
        } > "$HOME/.tmux.conf"
        chown "$UID:$GID" "$HOME/.tmux.conf"
    fi

    # --- Session Mirroring (Tmux) ---
    echo ">> Starting Shared Session (Tmux)..."
    
    # 1. Create a DETACHED tmux session named 'gemini' running the user's command
    # We must run this as the user so they own the session socket
    gosu "$TARGET_USER" tmux new-session -d -s gemini "$@"
    
    # 2. Start Web Terminal (ttyd) in BACKGROUND
    # It attaches to the 'gemini' session
    # -p 3000: Port
    # -W: Writable
    echo ">> Starting ttyd on port 3000..."
    ttyd -p 3000 -W gosu "$TARGET_USER" tmux attach -t gemini &
    
    echo ">> Web Terminal active at http://<IP>:3000"
    echo ">> Attaching local session..."
    
    # 3. Attach the Foreground (Desktop) to the same session
    # We DO NOT use 'exec' here so we can catch the exit and clean up
    if [ -t 0 ]; then
        gosu "$TARGET_USER" tmux attach -t gemini
    else
        echo ">> Detached mode detected. keeping container alive..."
        # Wait for the tmux session to end
        while gosu "$TARGET_USER" tmux has-session -t gemini 2>/dev/null; do
            sleep 1
        done
    fi
    
    # Cleanup on exit
    echo ">> Session ended. Stopping remote services..."
    pkill tailscaled || true
    pkill ttyd || true
    exit 0
fi

# Export HOME so the child process uses the correct directory
export HOME

# Execute (Standard Mode)
exec gosu "$TARGET_USER" "$@"
