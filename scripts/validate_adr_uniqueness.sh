#!/bin/bash
# Standardized script to validate ADR uniqueness.
# Returns 0 if all ADR numbers are unique, 1 otherwise.

set -euo pipefail

ADR_DIR="adr"

if [ ! -d "$ADR_DIR" ]; then
    echo "Error: ADR directory '$ADR_DIR' not found." >&2
    exit 1
fi

DUPLICATES=$(ls "$ADR_DIR"/*.md | cut -d/ -f2 | cut -d- -f1 | sort | uniq -d)

if [ -n "$DUPLICATES" ]; then
    echo "::error::Duplicate ADR numbers found: $DUPLICATES" >&2
    exit 1
fi

echo "All ADR numbers are unique."
