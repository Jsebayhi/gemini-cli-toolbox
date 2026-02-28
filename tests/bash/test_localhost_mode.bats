#!/usr/bin/env bats

load "test_helper.bash"

setup() {
    load "test_helper.bash"
    setup_test_env
    
    # Mock 'docker'
    mock_docker
}

teardown() {
    teardown_test_env
}

@test "gemini-toolbox --no-vpn uses bridge network and maps port" {
    cd "${TEST_TEMP_DIR}"

    run gemini-toolbox --no-vpn --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "docker run --rm -d --name gem-"
    assert_line --partial "--network=bridge"
    assert_line --partial "-p 127.0.0.1:0:3000"
}

@test "gemini-toolbox --no-vpn starts hub in no-vpn mode if needed" {
    # We need to make gemini-toolbox believe the hub is NOT running.
    # mock_docker returns nothing for 'ps', so it should attempt to start it.
    
    # We can't easily mock the gemini-hub script without overwriting it in /code/bin.
    # But gemini-hub itself calls docker, which is mocked!
    # So we check if gemini-hub container was started.

    cd "${TEST_TEMP_DIR}"
    
    run gemini-toolbox --no-vpn --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    # gemini-hub starts a container named 'gemini-hub-service'
    assert_line --partial "docker run --rm -d --name gemini-hub-service"
    assert_line --partial "GEMINI_HUB_NO_VPN=true"
}

@test "gemini-hub --no-vpn starts without a key" {
    run gemini-hub --no-vpn status
    
    assert_success
    assert_line "Gemini Hub is not running."
}

@test "gemini-hub fails without a key if --no-vpn is missing" {
    # Ensure key is NOT in environment
    unset GEMINI_REMOTE_KEY
    run gemini-hub
    
    assert_failure
    assert_line --partial "TAILSCALE_KEY is required for the Hub (or use --no-vpn)."
}
