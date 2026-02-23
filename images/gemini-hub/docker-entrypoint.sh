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

    # 1. Start Tailscale Daemon (Userspace Networking)
    # --tun=userspace-networking: Avoids needing /dev/net/tun device
    # --statedir: Using /var/lib/tailscale for persistence (mapped to named volume)
    # --socket: Custom socket path to allow easy permission management
    log_info "Starting Tailscaled..."
    mkdir -p /var/lib/tailscale
    tailscaled --tun=userspace-networking --statedir=/var/lib/tailscale --socket=/tmp/tailscaled.sock &
    sleep 3

    # 2. Authenticate
    if [ -z "${TAILSCALE_AUTH_KEY:-}" ]; then
        log_error "TAILSCALE_AUTH_KEY is missing."
        exit 1
    fi

    log_info "Authenticating with Tailscale..."
    # Fixed hostname for consistent DNS (http://gemini-hub:8888)
    # --force-reauth: Aggressively reclaim the 'gemini-hub' name if state was lost
    local HOSTNAME="gemini-hub"
    tailscale --socket=/tmp/tailscaled.sock up --authkey="$TAILSCALE_AUTH_KEY" --hostname="$HOSTNAME" --force-reauth

    log_info "Gemini Hub Online: http://$HOSTNAME:8888"
    
    # 2.1 User Creation: Create a non-root user matching the host UID/GID
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

    # 2.2 Tailscale Socket Permissions
    # Allow the non-root user to talk to the Tailscale daemon
    chown "$TARGET_USER" /tmp/tailscaled.sock

    # 2.3 Docker-out-of-Docker Setup
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
