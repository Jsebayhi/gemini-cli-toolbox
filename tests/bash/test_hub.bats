#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
}

teardown() {
    teardown_test_env
}

@test "gemini-hub --help returns 0" {
    run gemini-hub --help
    assert_success
    assert_output --partial "Usage: gemini-hub"
}

@test "gemini-hub requires auth key" {
    run gemini-hub
    assert_failure
    assert_output --partial "Error: TAILSCALE_KEY is required"
}

@test "gemini-hub with key calls docker run" {
    run gemini-hub --key tskey-auth-123
    assert_success
    run grep "docker run" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "gemini-hub stop command calls docker stop" {
    run gemini-hub stop
    assert_success
    run grep "docker stop gemini-hub-service" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "gemini-hub uses host networking" {
    run gemini-hub --key tskey-auth-123
    assert_success
    run grep "\-\-net=host" "$MOCK_DOCKER_LOG"
    assert_success
}
