#!/bin/bash
# Patch Gemini CLI to respect GEMINI_CLI_IDE_SERVER_HOST for VS Code integration.
#
# This script handles both traditional multi-file (dist/src/...) 
# and modern bundled (bundle/gemini.js) structures.

set -euo pipefail

NPM_CONFIG_PREFIX="${1:-/opt/npm-global}"
PATCHED=0

echo "Applying IDE host detection patch in $NPM_CONFIG_PREFIX..."

CANDIDATES=$(find "$NPM_CONFIG_PREFIX" -name "gemini.js" -o -name "ide-connection-utils.js" -o -name "ide-client.js" | 
    grep -E "bundle/gemini.js|dist/src/ide/ide-connection-utils.js|dist/src/ide/ide-client.js" || true)

if [ -n "$CANDIDATES" ]; then
    for F in $CANDIDATES; do
        # Robust regex for function signature (handles optional export and whitespace)
        if grep -qE "(export[[:space:]]+)?function[[:space:]]+getIdeServerHost[[:space:]]*\([[:space:]]*\)[[:space:]]*\{" "$F"; then
            echo "Applying patch to $F..."
            sed -i "s/\(\(export[[:space:]]\+\)\?function[[:space:]]\+getIdeServerHost[[:space:]]*([[:space:]]*)[[:space:]]*{\)/& if (process.env.GEMINI_CLI_IDE_SERVER_HOST) return process.env.GEMINI_CLI_IDE_SERVER_HOST;/" "$F"
            PATCHED=1
        elif grep -q "return isInContainer ? 'host.docker.internal' : '127.0.0.1'" "$F"; then
            echo "Applying legacy patch to $F..."
            sed -i "s/return isInContainer ? 'host.docker.internal' : '127.0.0.1'/return process.env.GEMINI_CLI_IDE_SERVER_HOST || (isInContainer ? 'host.docker.internal' : '127.0.0.1')/" "$F"
            PATCHED=1
        fi
    done
fi

if [ "$PATCHED" -eq 0 ]; then
    echo "Error: Failed to patch IDE host detection logic. Candidates checked: $CANDIDATES" >&2
    exit 1
fi

echo "Successfully patched IDE host detection."
