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
    mkdir -p "$TEST_TEMP_DIR/ws1" "$TEST_TEMP_DIR/ws2"
    run gemini-hub --key tskey-123 --workspace "$TEST_TEMP_DIR/ws1" --workspace "$TEST_TEMP_DIR/ws2"
    assert_success
    run grep "HUB_ROOTS=.*ws1.*ws2" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Hub Journey: Config Root Override" {
    mkdir -p "$TEST_TEMP_DIR/custom-configs"
    run gemini-hub --key tskey-123 --config-root "$TEST_TEMP_DIR/custom-configs"
    assert_success
    run grep "HOST_CONFIG_ROOT=.*custom-configs" "$MOCK_DOCKER_LOG"
    assert_success
}
