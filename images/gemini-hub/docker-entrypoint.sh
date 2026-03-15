#!/bin/bash
set -e

main() {
    # Logging Configuration
    # 0=ERROR, 1=WARN, 2=INFO, 3=DEBUG
    local LOG_LEVEL=2
    [ "${DEBUG:-false}" = "true" ] && LOG_LEVEL=3

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

    # 1. User Creation: Create a non-root user matching the host UID/GID
    # This allows the Flask app to safely operate on host-mounted volumes
    local TARGET_UID=${HOST_UID:-1000}

    local TARGET_GID=${HOST_GID:-1000}
    local USER="gemini"
    
    if ! getent group "$TARGET_GID" >/dev/null 2>&1; then
        groupadd -g "$TARGET_GID" "$USER" >/dev/null 2>&1
    fi

    if ! getent passwd "$TARGET_UID" >/dev/null 2>&1; then
        useradd -u "$TARGET_UID" -g "$TARGET_GID" -m -s /bin/bash "$USER" >/dev/null 2>&1
    fi

    local TARGET_USER
    TARGET_USER=$(getent passwd "$TARGET_UID" | cut -d: -f1)
    local HOME_DIR="/home/$TARGET_USER"

    # 2.2 Home Directory Permissions (Surgical Fix)
    is_mountpoint() {
        if command -v mountpoint >/dev/null 2>&1; then
            mountpoint -q "$1"
            return $?
        fi
        grep -q " $1 " /proc/self/mounts 2>/dev/null
    }

    # Fix any root-owned sub-items in the home directory (e.g., parents of mount points)
    # Use -xdev to avoid traversing into mount points.
    if [ -d "$HOME_DIR" ] && find "$HOME_DIR" -xdev -user root -print -quit | grep -q .; then
        log_info "Fixing root-owned home sub-items (non-recursive)..."
        find "$HOME_DIR" -xdev -user root | while read -r item; do
            if ! is_mountpoint "$item"; then
                chown -h "$TARGET_UID:$TARGET_GID" "$item"
            fi
        done
    fi

    # 2. Docker-out-of-Docker Setup
    local DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
    if [ -n "${HOST_DOCKER_GID:-}" ] && [ -S "$DOCKER_SOCK" ]; then
        if ! getent group "$HOST_DOCKER_GID" >/dev/null 2>&1; then
            groupadd -g "$HOST_DOCKER_GID" host-docker >/dev/null 2>&1
        fi
        usermod -aG "$HOST_DOCKER_GID" "$TARGET_USER" >/dev/null 2>&1
    fi

    # 3. Start Flask App
    # We use gosu to drop privileges for the Flask app
    exec gosu "$TARGET_USER" python run.py
}

# Entry point guard
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]]; then
    main "$@"
fi
