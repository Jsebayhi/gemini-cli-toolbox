#!/usr/bin/env bash

# Load bats-support and bats-assert
load 'libs/bats-support/load'
load 'libs/bats-assert/load'

# Set up test environment
setup_test_env() {
    export TEST_TEMP_DIR="$(mktemp -d)"
    export HOME="$TEST_TEMP_DIR"
    export MOCK_DOCKER_LOG="$TEST_TEMP_DIR/docker.log"
    export MOCK_GIT_LOG="$TEST_TEMP_DIR/git.log"
    touch "$MOCK_DOCKER_LOG" "$MOCK_GIT_LOG"
    
    # Path to real project root
    export PROJECT_ROOT="/code"
    
    # Create a fresh git repo for tests
    cd "$TEST_TEMP_DIR"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"
    git commit -q --allow-empty -m "Initial commit"

    # Setup bin for mocks
    mkdir -p "$TEST_TEMP_DIR/bin"
    export PATH="$TEST_TEMP_DIR/bin:$PROJECT_ROOT/bin:$PATH"

    # Fix dubious ownership for git commands in container
    git config --global --add safe.directory "$TEST_TEMP_DIR"
}

teardown_test_env() {
    rm -rf "$TEST_TEMP_DIR"
}

# Simple Mocking functions
mock_docker() {
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
case "\$1" in
    inspect) exit 1 ;;
    ps) exit 0 ;;
    *) exit 0 ;;
esac
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
}

mock_git() {
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
echo "git \$*" >> "$MOCK_GIT_LOG"
# Always succeed to satisfy script guards
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
}
