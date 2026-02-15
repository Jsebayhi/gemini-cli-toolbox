#!/usr/bin/env bash

# Load bats-support and bats-assert
load 'libs/bats-support/load'
load 'libs/bats-assert/load'

# Set up test environment
setup_test_env() {
    export TEST_TEMP_DIR="$(mktemp -d)"
    export HOME="$TEST_TEMP_DIR"
    export GEMINI_CONF_DIR="$TEST_TEMP_DIR/.gemini"
    mkdir -p "$GEMINI_CONF_DIR"
    
    # Mock bin directory
    export PROJECT_ROOT="$(pwd)"
    export BIN_DIR="$PROJECT_ROOT/bin"
    
    # Path to scripts
    export TOOLBOX="$BIN_DIR/gemini-toolbox"
    export HUB="$BIN_DIR/gemini-hub"
    
    # Ensure bin/ is in path for mocks
    mkdir -p "$TEST_TEMP_DIR/bin"
    export PATH="$TEST_TEMP_DIR/bin:$PATH"
}

teardown_test_env() {
    rm -rf "$TEST_TEMP_DIR"
}

# Mocking docker command
mock_docker() {
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
echo "docker \$*" >> "$TEST_TEMP_DIR/docker_calls.log"
case "\$1" in
    inspect)
        exit 1 # Simulate image not found locally by default
        ;;
    ps)
        exit 0
        ;;
    *)
        exit 0
        ;;
esac
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
}

# Mocking git command
mock_git() {
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
exit 1 # Simulate not in a git repo by default
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
}
