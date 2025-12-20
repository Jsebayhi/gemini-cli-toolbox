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

# Export HOME so the child process uses the correct directory
export HOME

# Execute
exec gosu "$UID:$GID" "$@"
