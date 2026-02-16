#!/bin/bash
set -eu

# 0. Entrypoint Logic (Source-safe)
main() {
    local TARGET_UID=${DEFAULT_UID:-1000}
    local TARGET_GID=${DEFAULT_GID:-1000}
    local USER=${DEFAULT_USERNAME:-gemini}
    local HOME=${DEFAULT_HOME_DIR:-/home/$USER}
    local DEBUG=${DEBUG:-false}

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
    if ! getent group "$TARGET_GID" >/dev/null 2>&1; then
        groupadd -g "$TARGET_GID" "$USER" >&3 2>&4
    fi

    # Create User if missing
    if ! getent passwd "$TARGET_UID" >/dev/null 2>&1; then
        useradd -u "$TARGET_UID" -g "$TARGET_GID" -m -d "$HOME" -s /bin/bash "$USER" >&3 2>&4
    fi

    # Identify the actual username for the UID (in case it pre-existed)
    local TARGET_USER
    TARGET_USER=$(getent passwd "$TARGET_UID" | cut -d: -f1)

    # Fix permissions
    mkdir -p "$HOME"
    chown -R "$TARGET_UID:$TARGET_GID" "$HOME"

    # --- Docker-out-of-Docker Setup ---
    local DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
    if [ -n "${HOST_DOCKER_GID:-}" ] && [ -S "$DOCKER_SOCK" ]; then
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

    # --- Tmux Configuration ---
    # We use Tmux by default so sessions are always re-attachable (e.g. after terminal crash)
    # Users can opt-out by setting GEMINI_TOOLBOX_TMUX=false (or using --no-tmux flag)
    local USE_TMUX="${GEMINI_TOOLBOX_TMUX:-true}"

    if [ "$USE_TMUX" = "true" ]; then
        if [ ! -f "$HOME/.tmux.conf" ]; then
            if [ "$DEBUG" = "true" ]; then
                echo ">> Generating default .tmux.conf..." >&3
            fi
            {
                echo "set -g mouse on"
                echo "set -g history-limit 50000"
            } > "$HOME/.tmux.conf"
            chown "$TARGET_UID:$TARGET_GID" "$HOME/.tmux.conf"
        fi

        # 1. Create a DETACHED tmux session named 'gemini' running the user's command
        if [ "$DEBUG" = "true" ]; then
            echo ">> Starting Shared Session (Tmux) for: $*" >&3
        fi
        gosu "$TARGET_USER" tmux new-session -d -s gemini "$@"
    fi

    # --- Remote Access (Tailscale) ---
    if [ -n "${TAILSCALE_AUTH_KEY:-}" ]; then
        echo ">> Initializing Remote Access Mode (Tailscale)..."
        # Start tailscaled in the background
        tailscaled --tun=userspace-networking --statedir=/tmp/tailscale &
        
        # Wait for daemon to be ready
        sleep 2
        
        # Generate meaningful hostname from project directory
        local TS_HOSTNAME
        if [ -n "${GEMINI_SESSION_ID:-}" ]; then
            TS_HOSTNAME="${GEMINI_SESSION_ID}"
        else
            local RAW_PROJ="${GEMINI_PROJECT_NAME:-$(basename "$(pwd)")}"
            local RAW_TYPE="${GEMINI_SESSION_TYPE:-unknown}"
            
            local CLEAN_PROJ
            CLEAN_PROJ=$(echo "$RAW_PROJ" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')
            local CLEAN_TYPE
            CLEAN_TYPE=$(echo "$RAW_TYPE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')
            local UNIQUE_SUFFIX
            UNIQUE_SUFFIX=$(hostname | cut -c1-4)
            
            TS_HOSTNAME="gem-${CLEAN_PROJ}-${CLEAN_TYPE}-${UNIQUE_SUFFIX}"
        fi
        
        # Authenticate and bring up the node
        echo ">> Registering VPN Node: ${TS_HOSTNAME}"
        tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname="${TS_HOSTNAME}"
        echo ">> Remote Access Active."
        
        # 2. Start Web Terminal (ttyd) in BACKGROUND
        echo ">> Starting ttyd on port 3000..."
        ttyd -p 3000 -W gosu "$TARGET_USER" tmux attach -t gemini &
        echo ">> Web Terminal active at http://<IP>:3000"
    fi

    # --- Execution ---
    if [ "$USE_TMUX" = "true" ]; then
        echo ">> Attaching to session (Tmux)..."
        if [ -t 0 ]; then
            exec gosu "$TARGET_USER" tmux attach -t gemini
        else
            echo ">> Detached mode detected. Keeping container alive..."
            while gosu "$TARGET_USER" tmux has-session -t gemini 2>/dev/null; do
                sleep 1
            done
        fi
        
        # Cleanup on exit
        if [ -n "${TAILSCALE_AUTH_KEY:-}" ]; then
            echo ">> Session ended. Stopping remote services..."
            pkill tailscaled || true
            pkill ttyd || true
        fi
        exit 0
    fi

    # Export HOME so the child process uses the correct directory
    export HOME

    # Execute (No-Tmux Mode)
    exec gosu "$TARGET_USER" "$@"
}

# Entry point guard
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]]; then
    main "$@"
fi
