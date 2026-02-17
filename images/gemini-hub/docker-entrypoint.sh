#!/bin/bash
set -e

main() {
    # Logging Configuration
    # 0=ERROR, 1=WARN, 2=INFO, 3=DEBUG
    local LOG_LEVEL=2
    [ "${DEBUG:-false}" = "true" ] && LOG_LEVEL=3

    # Internal logging FD (Defaults to 2/stderr)
    local _LOG_FD=${GEMINI_LOG_FD:-2}

    _log() {
        local level_name="$1"
        local level_val="$2"
        shift 2
        if [ "$LOG_LEVEL" -ge "$level_val" ]; then
            if [ "$level_val" -eq 0 ]; then
                echo "Error: $*" >&"$_LOG_FD"
            elif [ "$level_val" -eq 1 ]; then
                echo "Warning: $*" >&"$_LOG_FD"
            else
                echo ">> $*" >&"$_LOG_FD"
            fi
        fi
    }

    log_error() { _log "ERROR" 0 "$@"; }
    log_warn()  { _log "WARN"  1 "$@"; }
    log_info()  { _log "INFO"  2 "$@"; }
    log_debug() { _log "DEBUG" 3 "$@"; }

    # 1. Start Tailscale Daemon (Userspace Networking)
    # --tun=userspace-networking: Avoids needing /dev/net/tun device (sometimes)
    # --statedir: Mapped to named volume (/var/lib/tailscale) to persist Device ID
    log_info "Starting Tailscaled..."
    tailscaled --tun=userspace-networking --statedir=/var/lib/tailscale &
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
    tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname="$HOSTNAME" --force-reauth

    log_info "Gemini Hub Online: http://$HOSTNAME:8888"

    # 3. Start Flask App
    exec python run.py
}

# Entry point guard
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]]; then
    main "$@"
fi
