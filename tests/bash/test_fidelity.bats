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

@test "Fidelity: gemini-toolbox --bash constructed command check" {
    # Run the toolbox in bash mode
    run "$TOOLBOX" --bash
    assert_success
    
    # Check the log file content
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run cat "$TEST_TEMP_DIR/docker_calls.log"
    assert_output --partial "docker 'run' '--rm'"
    
    # Check for networking (default is host)
    assert_output --partial "'--net=host'"
    
    # Check for volume mounts (e.g., config and project dir)
    assert_output --partial "'--volume' '$HOME/.gemini:/home/gemini/.gemini'"
    
    # Check for the correct image and entrypoint
    assert_output --partial "'--entrypoint' '/usr/local/bin/docker-entrypoint.sh'"
    assert_output --partial "'bash'"
}

@test "Fidelity: gemini-toolbox --remote constructing correct bridge network" {
    # Mocking id to return 1000 for consistent volume path checks if needed
    run "$TOOLBOX" --remote tskey-auth-1234 --bash
    assert_success
    
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run cat "$TEST_TEMP_DIR/docker_calls.log"
    
    # In remote mode, network must be bridge
    assert_output --partial "'--network=bridge'"
    
    # Check for Tailscale env var
    assert_output --partial "'--env' 'TAILSCALE_AUTH_KEY=tskey-auth-1234'"
    
    # Check for Cap Add and Device
    assert_output --partial "'--cap-add=NET_ADMIN'"
    assert_output --partial "'--device' '/dev/net/tun'"
}

@test "Fidelity: gemini-hub start constructed command check" {
    run "$HUB" --key tskey-hub-1234
    assert_success
    
    [ -f "$TEST_TEMP_DIR/docker_calls.log" ]
    run cat "$TEST_TEMP_DIR/docker_calls.log"
    
    # Hub always uses host network
    assert_output --partial "'--net=host'"
    
    # Verify environment variables passed to Hub
    assert_output --partial "'--env' 'TAILSCALE_AUTH_KEY=tskey-hub-1234'"
    assert_output --partial "'--name' 'gemini-hub-service'"
}
