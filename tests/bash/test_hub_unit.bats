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

@test "Hub main: dynamic branch tagging" {
    source_hub
    # Mock git to return a feature branch
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"rev-parse --abbrev-ref HEAD"* ]]; then echo "feature/fix-1"; exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
    
    # Mock docker to succeed on inspect and log run
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "run" ]]; then echo "docker \$*" >> "$MOCK_DOCKER_LOG"; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"

    run bash -x -c "source $PROJECT_ROOT/bin/gemini-hub; main --key tskey-123 --detach"
    assert_success
    run grep "gemini-cli-toolbox/hub:latest-feature-fix-1" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: stop command failure" {
    source_hub
    # Mock hub as running (container exists in ps -a)
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "ps" && "\$*" == *"--format {{.Names}}"* ]]; then echo "gemini-hub-service"; exit 0; fi
if [[ "\$1" == "stop" ]]; then exit 1; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main stop
    assert_failure
    assert_output --partial "Error: Failed to stop Gemini Hub service"
}

@test "Hub main: error on missing key" {
    source_hub
    # Ensure env var is NOT set
    unset GEMINI_REMOTE_KEY
    run main
    assert_failure
    assert_output --partial "Error: TAILSCALE_KEY is required"
}

@test "Hub main: config root fallback to .gemini-profiles" {
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

@test "Hub main: check toolbox script mount" {
    source_hub
    mock_docker
    run main --key tskey-123
    assert_success
    # By default in tests, bin/gemini-toolbox exists next to gemini-hub
    run grep "/usr/local/bin/gemini-toolbox" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: multiple workspace roots logic" {
    source_hub
    mock_docker
    local ws1="$TEST_TEMP_DIR/ws1"
    local ws2="$TEST_TEMP_DIR/ws2"
    mkdir -p "$ws1" "$ws2"
    
    # Also test duplicate workspace root suppression
    run main --key tskey-123 --workspace "$ws1" --workspace "$ws2" --workspace "$ws1"
    assert_success
    run grep "HUB_ROOTS=$ws1:$ws2" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: auto-shutdown and no-prune flags" {
    source_hub
    mock_docker
    run main --key tskey-123 --auto-shutdown --no-worktree-prune
    assert_success
    run grep "HUB_AUTO_SHUTDOWN=1" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "HUB_WORKTREE_PRUNE_ENABLED=false" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: image override" {
    source_hub
    mock_docker
    run main --key tskey-123 --image my-custom-hub
    assert_success
    run grep "my-custom-hub" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub main: status running" {
    source_hub
    # Mock hub as running
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == *"ps -aq"* ]]; then echo "cont123"; exit 0; fi
if [[ "\$*" == *"inspect"* ]]; then echo "true"; exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main status
    assert_success
    assert_output --partial "Gemini Hub is running (ID: cont123)"
}

@test "Hub main: status not running" {
    source_hub
    # Mock hub as NOT running
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == *"ps -aq"* ]]; then exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main status
    assert_success
    assert_output --partial "Gemini Hub is not running."
}

@test "Hub main: status stopped" {
    source_hub
    # Mock hub as existing but NOT running
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == *"ps -aq"* ]]; then echo "cont123"; exit 0; fi
if [[ "\$*" == *"inspect"* ]]; then echo "false"; exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main status
    assert_success
    assert_output --partial "Gemini Hub is not running."
}

@test "Hub main: stop command fails but container exists" {
    source_hub
    # Mock container exists but stop fails
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == *"ps -a --format"* ]]; then echo "gemini-hub-service"; exit 0; fi
if [[ "\$1" == "stop" ]]; then exit 1; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main stop
    assert_failure
    assert_output --partial "Error: Failed to stop Gemini Hub service"
}

@test "Hub main: smart restart interactive logic" {
    # This logic is partially covered by non-interactive Hub Journey tests.
    # Interactive tests require a real TTY which is hard to mock in BATS.
    skip "Requires real TTY for [ -t 0 ]"
}
