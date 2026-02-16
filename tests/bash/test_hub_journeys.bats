#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
}

teardown() {
    teardown_test_env
}

@test "Hub Journey: Basic Start" {
    run gemini-hub --key tskey-auth-123
    assert_success
    run grep "docker run .* gemini-cli-toolbox/hub:latest" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub Journey: Stop Command" {
    run gemini-hub stop
    assert_success
    run grep "docker stop gemini-hub-service" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub Journey: Workspace Mounts" {
    local ws1="$TEST_TEMP_DIR/ws1"
    local ws2="$TEST_TEMP_DIR/ws2"
    mkdir -p "$ws1" "$ws2"
    run gemini-hub --key tskey-123 --workspace "$ws1" --workspace "$ws2"
    assert_success
    run grep "HUB_ROOTS=.*ws1.*ws2" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub Journey: Config Root Override" {
    local custom="$TEST_TEMP_DIR/custom-configs"
    mkdir -p "$custom"
    run gemini-hub --key tskey-123 --config-root "$custom"
    assert_success
    run grep "HOST_CONFIG_ROOT=.*custom-configs" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub Journey: Smart Restart - Merge Roots (Non-interactive)" {
    # Use paths within TEST_TEMP_DIR to ensure they exist and are accessible
    local old_root="$TEST_TEMP_DIR/old-root"
    local new_root="$TEST_TEMP_DIR/new-root"
    mkdir -p "$old_root" "$new_root"
    
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
case "\$*" in
    "ps"* ) echo "gemini-hub-service"; exit 0 ;;
    "inspect"* ) echo "HUB_ROOTS=$old_root"; exit 0 ;;
    * ) echo "docker \$*" >> "$MOCK_DOCKER_LOG"; exit 0 ;;
esac
EOF

    gemini-hub --key tskey-123 --workspace "$new_root"
    
    grep "docker stop gemini-hub-service" "$MOCK_DOCKER_LOG"
    # Order is new:old because of how the script appends/merges
    grep "HUB_ROOTS=$new_root:$old_root" "$MOCK_DOCKER_LOG"
}

@test "Hub Journey: Smart Restart - Already Covered" {
    local covered="$TEST_TEMP_DIR/covered"
    mkdir -p "$covered"
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
case "\$*" in
    "ps"* ) echo "gemini-hub-service"; exit 0 ;;
    "inspect"* ) echo "HUB_ROOTS=$covered"; exit 0 ;;
esac
EOF
    run gemini-hub --key tskey-123 --workspace "$covered"
    assert_success
    assert_output --partial "Active Hub already covers all requested workspaces"
}

@test "Hub Journey: Workspace does not exist (Warning)" {
    run gemini-hub --key tskey-123 --workspace "$TEST_TEMP_DIR/non-existent"
    assert_success
    assert_output --partial "Warning: Workspace root"
}

@test "Hub Journey: Stop Hub not running" {
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "stop" ]]; then exit 1; fi
EOF
    run gemini-hub stop
    assert_success
    assert_output --partial "Hub is not running"
}

@test "Hub Journey: Environment Propagation" {
    TERM="xterm-256color" COLORTERM="truecolor" run gemini-hub --key tskey-123
    assert_success
    
    run grep "ENV: TERM=xterm-256color" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "ENV: COLORTERM=truecolor" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub Journey: Multiple Workspaces" {
    local ws1="$TEST_TEMP_DIR/ws1"
    local ws2="$TEST_TEMP_DIR/ws2"
    mkdir -p "$ws1" "$ws2"
    
    run gemini-hub --key tskey-123 --workspace "$ws1" --workspace "$ws2" --workspace "$ws1"
    assert_success
    run grep "HUB_ROOTS=$ws1:$ws2" "$MOCK_DOCKER_LOG"
    assert_success
}
