#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
}

teardown() {
    teardown_test_env
}

source_hub() {
    export HOME="$TEST_TEMP_DIR"
    source gemini-hub
}

@test "Hub show_help function prints usage" {
    source_hub
    run show_help
    assert_success
    assert_output --partial "Usage: gemini-hub"
}

@test "Hub main: image detection logic (local exists)" {
    source_hub
    # Mock docker image inspect to return 0
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then exit 0; fi
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    run main --key tskey-123
    assert_success
    run grep "gemini-cli-toolbox/hub:latest" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: image detection logic (local missing)" {
    source_hub
    # Mock docker image inspect to return 1
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then exit 1; fi
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    run main --key tskey-123
    assert_success
    run grep "jsebayhi/gemini-cli-toolbox:latest-hub" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: config root fallback" {
    source_hub
    local profiles_dir="$TEST_TEMP_DIR/.gemini-profiles"
    mkdir -p "$profiles_dir"
    # Ensure default config root does NOT exist
    rm -rf "$HOME/.gemini/configs"
    
    mock_docker
    run main --key tskey-123
    assert_success
    run grep "HOST_CONFIG_ROOT=$profiles_dir" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: workspace root existence warning" {
    source_hub
    mock_docker
    run main --key tskey-123 --workspace "/tmp/non-existent-$(date +%s)"
    assert_success
    assert_output --partial "Warning: Workspace root"
    assert_output --partial "does not exist. Skipping."
}

@test "Hub main: expiry days env propagation" {
    source_hub
    export GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS=10
    export GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS=20
    export GEMINI_WORKTREE_ORPHAN_EXPIRY_DAYS=30
    
    mock_docker
    run main --key tskey-123
    assert_success
    
    run grep "GEMINI_WORKTREE_HEADLESS_EXPIRY_DAYS=10" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "GEMINI_WORKTREE_BRANCH_EXPIRY_DAYS=20" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "GEMINI_WORKTREE_ORPHAN_EXPIRY_DAYS=30" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: check toolbox script mount" {
    source_hub
    mock_docker
    run main --key tskey-123
    assert_success
    # By default in tests, bin/gemini-toolbox exists next to gemini-hub
    run grep "/usr/local/bin/gemini-toolbox" "$MOCK_DOCKER_LOG"
    assert_success
}
