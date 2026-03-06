#!/bin/bash
# Patch Gemini CLI internal logic to overcome hardcoded limitations.
#
# This script handles both traditional multi-file (dist/src/...) 
# and modern bundled (bundle/gemini.js) structures.

set -euo pipefail

NPM_CONFIG_PREFIX="${1:-/opt/npm-global}"
PATCHED_IDE=0
PATCHED_RETRY=0

echo "Starting Gemini CLI source code patching in $NPM_CONFIG_PREFIX..."

# 1. Patch IDE Host Detection
# Target: [export] function getIdeServerHost() { ... }
# We inject an early return to respect GEMINI_CLI_IDE_SERVER_HOST.
IDE_CANDIDATES=$(find "$NPM_CONFIG_PREFIX" -name "gemini.js" -o -name "ide-connection-utils.js" -o -name "ide-client.js" | \
    grep -E "bundle/gemini.js|dist/src/ide/ide-connection-utils.js|dist/src/ide/ide-client.js" || true)

if [ -n "$IDE_CANDIDATES" ]; then
    for F in $IDE_CANDIDATES; do
        # Robust regex for function signature (handles optional export and whitespace)
        if grep -qE "(export[[:space:]]+)?function[[:space:]]+getIdeServerHost[[:space:]]*\([[:space:]]*\)[[:space:]]*\{" "$F"; then
            echo "Applying patch for getIdeServerHost to $F..."
            sed -i "s/\(\(export[[:space:]]\+\)\?function[[:space:]]\+getIdeServerHost[[:space:]]*([[:space:]]*)[[:space:]]*{\)/& if (process.env.GEMINI_CLI_IDE_SERVER_HOST) return process.env.GEMINI_CLI_IDE_SERVER_HOST;/" "$F"
            PATCHED_IDE=1
        elif grep -q "return isInContainer ? 'host.docker.internal' : '127.0.0.1'" "$F"; then
            echo "Applying legacy patch for getIdeServerHost to $F..."
            sed -i "s/return isInContainer ? 'host.docker.internal' : '127.0.0.1'/return process.env.GEMINI_CLI_IDE_SERVER_HOST || (isInContainer ? 'host.docker.internal' : '127.0.0.1')/" "$F"
            PATCHED_IDE=1
        fi
    done
fi

# 2. Patch Infinite Retry
# Target: message = messageLines.join("\n");
# We replace it with an early return to bypass the high-demand dialog.
RETRY_CANDIDATES=$(find "$NPM_CONFIG_PREFIX" -name "gemini.js" -o -name "useQuotaAndFallback.js" | \
    grep -E "bundle/gemini.js|dist/src/ui/hooks/useQuotaAndFallback.js" || true)

if [ -n "$RETRY_CANDIDATES" ]; then
    for F in $RETRY_CANDIDATES; do
        # Robust regex for messageLines.join (handles single/double quotes and whitespace)
        # We DO NOT use /g to avoid accidental over-patching in large bundles.
        # But we use it if we want to catch all instances of the join in the bundle 
        # (there are 4 identical ones in the preview bundle).
        if grep -qE "message[[:space:]]*=[[:space:]]*messageLines\.join\([^)]*\)" "$F"; then
            echo "Patching infinite retry in $F..."
            sed -i "s/message[[:space:]]*=[[:space:]]*messageLines\.join([^)]*)/return 'retry_always'/g" "$F"
            PATCHED_RETRY=1
        fi
    done
fi

# Verification
if [ "$PATCHED_IDE" -eq 0 ]; then
    echo "Error: Failed to patch IDE host detection logic. Candidates: $IDE_CANDIDATES" >&2
    exit 1
fi

if [ "$PATCHED_RETRY" -eq 0 ]; then
    echo "Error: Failed to patch infinite retry logic. Candidates: $RETRY_CANDIDATES" >&2
    exit 1
fi

echo "Successfully patched Gemini CLI."
