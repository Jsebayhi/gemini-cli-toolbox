#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    # We must mock git because the script checks for git on load if sourcing, or we need to ensure sourcing is safe.
    # The new pattern: sourcing shouldn't run logic.
    mock_docker
    mock_git
    
    # Source the toolbox script to test functions
    source "$TOOLBOX"
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
    # We need to mock id for the script to run
    # Since we are sourcing, we are in the test environment.
    # We can invoke main directly.
    
    run main --bash
    assert_success
    
    # Check docker calls
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run grep "docker run" "$TEST_TEMP_DIR/docker_calls.log"
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
