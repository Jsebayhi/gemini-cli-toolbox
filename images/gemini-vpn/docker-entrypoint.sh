#!/bin/sh
set -e

# Gemini VPN Sidecar Entrypoint
# Implementation of ADR-0059: Synchronized PID Lifecycle

# 0. Logging Setup
_log() {
    echo ">> [VPN] $*"
}

# 1. PID-1 Watchdog (Layer 1 Cleanup)
# This background process waits for PID 1 (the parent session) to exit.
# Since we use --pid container:ID, PID 1 is the parent's entrypoint.
watchdog() {
    _log "Watchdog active. Monitoring parent session (PID 1)..."
    # wait for PID 1 to disappear
    # We use a simple loop because 'tail --pid' might not be in the base image
    while [ -d "/proc/1" ]; do
        sleep 5
    done
    _log "Parent session (PID 1) has exited. Terminating sidecar..."
    # Kill the main tailscaled process to trigger container exit
    pkill tailscaled || exit 0
}

# Start watchdog in background
watchdog &

# 2. Start Tailscale
# We pass through all arguments to the original tailscaled/tailscale logic
# Most commonly used via 'tailscaled' directly or via arguments passed by docker run
_log "Starting Tailscale Sidecar..."

# If no arguments, or starting with '-', assume tailscaled
if [ $# -eq 0 ] || [ "${1#-}" != "$1" ]; then
    set -- tailscaled "$@"
fi

exec "$@"
