#!/bin/bash
set -eu

# 0. Entrypoint Logic (Source-safe)
main() {
    local TARGET_UID=${DEFAULT_UID:-1000}
    local TARGET_GID=${DEFAULT_GID:-1000}
    local USER=${DEFAULT_USERNAME:-gemini}
    local HOME=${DEFAULT_HOME_DIR:-/home/$USER}
    local DEBUG_MODE=${DEBUG:-false}

    # Logging Configuration
    # 0=ERROR, 1=WARN, 2=INFO, 3=DEBUG
    local LOG_LEVEL=2
    [ "$DEBUG_MODE" = "true" ] && LOG_LEVEL=3

    _log() {
        local level_val="$1"
        shift
        if [ "$LOG_LEVEL" -ge "$level_val" ]; then
            if [ "$level_val" -eq 0 ]; then
                echo "Error: $*" >&2
            elif [ "$level_val" -eq 1 ]; then
                echo "Warning: $*" >&2
            else
                echo ">> $*" >&2
            fi
        fi
    }

    log_error() { _log 0 "$@"; }
    log_warn()  { _log 1 "$@"; }
    log_info()  { _log 2 "$@"; }
    log_debug() { _log 3 "$@"; }

    # Create Group if missing
    if ! getent group "$TARGET_GID" >/dev/null 2>&1; then
        groupadd -g "$TARGET_GID" "$USER" >/dev/null 2>&1
    fi

    # Create User if missing
    if ! getent passwd "$TARGET_UID" >/dev/null 2>&1; then
        useradd -u "$TARGET_UID" -g "$TARGET_GID" -m -d "$HOME" -s /bin/bash "$USER" >/dev/null 2>&1
    fi

    # Identify the actual username for the UID (in case it pre-existed)
    local TARGET_USER
    TARGET_USER=$(getent passwd "$TARGET_UID" | cut -d: -f1)

    # Fix permissions
    # We no longer perform recursive chown on the home directory (ADR-0053).
    # Instead, we verify ownership and fail-fast if a mismatch is detected.
    mkdir -p "$HOME"

    is_mountpoint() {
        local mount_file=${MOCK_MOUNTS:-/proc/self/mounts}
        if command -v mountpoint >/dev/null 2>&1; then
            mountpoint -q "$1"
            return $?
        fi
        # Fallback for systems without mountpoint command (e.g. minimal images)
        # We check for the path surrounded by spaces in the mount list
        grep -q " $1 " "$mount_file" 2>/dev/null
    }

    local CURRENT_OWNER
    CURRENT_OWNER=$(stat -c %u:%g "$HOME")
    if [ "$CURRENT_OWNER" != "$TARGET_UID:$TARGET_GID" ]; then
        # SURGICAL FIX: If the directory is owned by root AND it's NOT a mount point,
        # it means it was created by the Dockerfile or Docker daemon (parent creation)
        # and not by the user. In this case, it's safe to fix the ownership of the
        # directory itself (non-recursively).
        if [ "$CURRENT_OWNER" = "0:0" ] && ! is_mountpoint "$HOME"; then
             log_info "Fixing root-owned home directory $HOME (non-recursive)..."
             chown "$TARGET_UID:$TARGET_GID" "$HOME"
             CURRENT_OWNER=$(stat -c %u:%g "$HOME")
        fi
    fi

    if [ "$CURRENT_OWNER" != "$TARGET_UID:$TARGET_GID" ]; then
        log_error "Permission mismatch detected on $HOME."
        log_error "The directory is owned by $CURRENT_OWNER but should be $TARGET_UID:$TARGET_GID."
        log_error "To fix this, run the following on your host machine:"
        log_error "  sudo chown -R \$(id -u):\$(id -g) ~/.gemini"
        exit 1
    fi

    # --- Docker-out-of-Docker Setup ---
    local DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
    if [ -n "${HOST_DOCKER_GID:-}" ] && [ -S "$DOCKER_SOCK" ]; then
        if [ "$DEBUG_MODE" = "true" ]; then
            log_debug "Setting up Docker Access (GID: $HOST_DOCKER_GID)..."
        fi

        # Check if a group with this GID already exists
        if ! getent group "$HOST_DOCKER_GID" >/dev/null 2>&1; then
            groupadd -g "$HOST_DOCKER_GID" host-docker >/dev/null 2>&1
        fi
        
        # Add user to the group
        usermod -aG "$HOST_DOCKER_GID" "$TARGET_USER" >/dev/null 2>&1
    fi

    # --- Tmux Configuration ---
    # We use Tmux by default so sessions are always re-attachable (e.g. after terminal crash)
    # Users can opt-out by setting GEMINI_TOOLBOX_TMUX=false (or using --no-tmux flag)
    local USE_TMUX="${GEMINI_TOOLBOX_TMUX:-true}"

    if [ "$USE_TMUX" = "true" ]; then
        if [ ! -f "$HOME/.tmux.conf" ]; then
            if [ "$DEBUG_MODE" = "true" ]; then
                log_debug "Generating default .tmux.conf..."
            fi
            {
                echo "set -g mouse on"
                echo "set -g history-limit 50000"
            } > "$HOME/.tmux.conf"
            chown "$TARGET_UID:$TARGET_GID" "$HOME/.tmux.conf"
        fi

        # 1. Create a DETACHED tmux session named 'gemini' running the user's command
        if [ "$DEBUG_MODE" = "true" ]; then
            log_debug "Starting Shared Session (Tmux) for: $*"
        fi
        gosu "$TARGET_USER" tmux new-session -d -s gemini "$@"
    fi

    # --- Web Terminal (ttyd) ---
    # We always start ttyd to provide web access for all connectivity tiers
    # (Localhost, VPN, and LAN). It attaches to the shared tmux session.
    log_info "Starting Web Terminal (ttyd) on port 3000..."
    ttyd -p 3000 -W gosu "$TARGET_USER" tmux attach -t gemini &

    # --- Execution ---
    if [ "$USE_TMUX" = "true" ]; then
        log_info "Attaching to session (Tmux)..."
        if [ -t 0 ]; then
            exec gosu "$TARGET_USER" tmux attach -t gemini
        else
            log_info "Detached mode detected. Keeping container alive..."
            while gosu "$TARGET_USER" tmux has-session -t gemini 2>/dev/null; do
                sleep 1
            done
        fi
        
        # Cleanup on exit
        log_info "Session ended. Stopping services..."
        pkill ttyd || true
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
