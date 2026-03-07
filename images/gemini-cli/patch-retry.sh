#!/bin/bash
# Patch Gemini CLI to return "retry_always" automatically for high-demand errors.
#
# This script handles both traditional multi-file (dist/src/...) 
# and modern bundled (bundle/gemini.js) structures.

set -euo pipefail

NPM_CONFIG_PREFIX="${1:-/opt/npm-global}"
PATCHED=0

echo "Applying Infinite Retry patch in $NPM_CONFIG_PREFIX..."

CANDIDATES=$(find "$NPM_CONFIG_PREFIX" -name "gemini.js" -o -name "useQuotaAndFallback.js" | 
    grep -E "bundle/gemini.js|dist/src/ui/hooks/useQuotaAndFallback.js" || true)

if [ -n "$CANDIDATES" ]; then
    for F in $CANDIDATES; do
        # Robust regex for messageLines.join (handles single/double quotes and whitespace)
        if grep -qE "message[[:space:]]*=[[:space:]]*messageLines\.join\([^)]*\)" "$F"; then
            echo "Applying patch to $F..."
            sed -i "s/message[[:space:]]*=[[:space:]]*messageLines\.join([^)]*)/return 'retry_always'/g" "$F"
            PATCHED=1
        fi
    done
fi

if [ "$PATCHED" -eq 0 ]; then
    echo "Error: Failed to patch infinite retry logic. Candidates checked: $CANDIDATES" >&2
    exit 1
fi

echo "Successfully patched infinite retry."
