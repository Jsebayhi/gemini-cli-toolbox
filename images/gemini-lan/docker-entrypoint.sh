#!/bin/sh
set -e

# Gemini LAN Sidecar Entrypoint
# Implementation of ADR-0059: Synchronized PID Lifecycle

# 0. Logging Setup
_log() {
    echo ">> [LAN] $*"
}

# 1. PID-1 Watchdog (Layer 1 Cleanup)
watchdog() {
    _log "Watchdog active. Monitoring parent session (PID 1)..."
    while [ -d "/proc/1" ]; do
        sleep 5
    done
    _log "Parent session (PID 1) has exited. Terminating sidecar..."
    pkill socat || exit 0
}

# Start watchdog in background
watchdog &

# 2. Start Socat Proxy
# We bridge external port 3000 to internal localhost:3000 (shared network)
_log "Starting LAN Proxy (0.0.0.0:3000 -> localhost:3000)..."
exec socat TCP-LISTEN:3000,fork,reuseaddr TCP:localhost:3000
