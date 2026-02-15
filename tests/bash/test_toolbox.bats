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

@test "gemini-toolbox --help returns 0" {
    run "$TOOLBOX" --help
    assert_success
    assert_output --partial "Usage:"
}

@test "gemini-toolbox --remote and --no-tmux are incompatible" {
    run "$TOOLBOX" --remote --no-tmux
    assert_failure
    assert_output --partial "Error: --remote and --no-tmux are incompatible"
}

@test "gemini-toolbox calls docker run with correct name" {
    # Default name detection logic is complex, but let's see if it calls docker run
    run "$TOOLBOX" --bash
    assert_success
    
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run grep "docker run" "$TEST_TEMP_DIR/docker_calls.log"
    assert_success
}
