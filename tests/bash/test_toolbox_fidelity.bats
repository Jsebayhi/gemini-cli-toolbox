#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
}

teardown() {
    teardown_test_env
}

@test "Command construction: gemini-toolbox --bash" {
    run gemini-toolbox --bash
    assert_success
    run grep "docker run .* bash" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Command construction: gemini-toolbox --remote (bridge network)" {
    # Unset TERM_PROGRAM to avoid VS Code detection which might force host network
    unset TERM_PROGRAM
    run gemini-toolbox --remote tskey-auth-123 --bash
    assert_success
    run grep "\-\-network=bridge" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Command construction: gemini-hub start" {
    run gemini-hub --key tskey-auth-123
    assert_success
    run grep "gemini-cli-toolbox/hub" "$MOCK_DOCKER_LOG"
    assert_success
}
