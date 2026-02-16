#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
}

teardown() {
    teardown_test_env
}

@test "gemini-toolbox --help returns 0" {
    run gemini-toolbox --help
    assert_success
    assert_output --partial "Usage: gemini-toolbox"
}

@test "gemini-toolbox --remote and --no-tmux are incompatible" {
    run gemini-toolbox --remote key --no-tmux
    assert_failure
    assert_output --partial "Error: --remote and --no-tmux are incompatible"
}

@test "gemini-toolbox calls docker run with correct name" {
    run gemini-toolbox chat
    assert_success
    run grep -E "docker run .* --name gem-" "$MOCK_DOCKER_LOG"
    assert_success
}
