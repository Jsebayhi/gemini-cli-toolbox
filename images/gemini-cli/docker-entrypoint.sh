#!/bin/sh
set -eu

UID=${DEFAULT_UID:-1000}
GID=${DEFAULT_GID:-1000}
USER=${DEFAULT_USERNAME:-gemini}
HOME=${DEFAULT_HOME_DIR:-/home/$USER}

# Create Group if missing
if ! getent group "$GID" >/dev/null 2>&1; then
    groupadd -g "$GID" "$USER"
fi

# Create User if missing
if ! getent passwd "$UID" >/dev/null 2>&1; then
    useradd -u "$UID" -g "$GID" -m -d "$HOME" -s /bin/bash "$USER"
fi

# Fix permissions
mkdir -p "$HOME"
chown -R "$UID:$GID" "$HOME"

# Export HOME so the child process uses the correct directory
export HOME

# Execute
exec gosu "$UID:$GID" "$@"
