#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
    # Source the real script
    source "$PROJECT_ROOT/bin/gemini-toolbox"
}

teardown() {
    teardown_test_env
}

@test "show_help function prints usage" {
    run show_help
    assert_success
    assert_output --partial "Usage: gemini-toolbox"
}

@test "main function runs correctly with --bash" {
    run main --bash
    assert_success
    run grep "docker run" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "setup_worktree function is defined" {
    run declare -f setup_worktree
    assert_success
}

@test "main fails with --remote and --no-tmux" {
    run main --remote tskey-auth --no-tmux
    assert_failure
    assert_output --partial "Error: --remote and --no-tmux are incompatible"
}
