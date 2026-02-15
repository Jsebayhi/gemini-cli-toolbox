#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
    mock_git
}

teardown() {
    teardown_test_env
}

@test "gemini-hub --help returns 0" {
    run "$HUB" --help
    assert_success
    assert_output --partial "Usage:"
}

@test "gemini-hub requires auth key" {
    run "$HUB"
    assert_failure
    assert_output --partial "Error: TAILSCALE_KEY is required"
}

@test "gemini-hub with key calls docker run" {
    # We need to ensure REPO_ROOT is correctly detected or at least doesn't crash realpath
    run "$HUB" --key tskey-auth-mock
    
    # Check if docker was called
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run grep "docker run" "$TEST_TEMP_DIR/docker_calls.log"
    assert_success
}

@test "gemini-hub stop command calls docker stop" {
    run "$HUB" stop
    assert_success
    assert_output --partial "Stopping Gemini Hub"
    
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run grep "docker stop" "$TEST_TEMP_DIR/docker_calls.log"
    assert_success
}

@test "gemini-hub uses host networking" {
    run "$HUB" --key tskey-auth-mock
    assert_success
    
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run grep "\-\-net=host" "$TEST_TEMP_DIR/docker_calls.log"
    assert_success
}
