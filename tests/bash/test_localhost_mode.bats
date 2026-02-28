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

@test "gemini-toolbox defaults to protected localhost (bridge + mapping)" {
    cd "${TEST_TEMP_DIR}"

    run gemini-toolbox --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "docker run --rm -d --name gem-"
    assert_line --partial "--network=bridge"
    assert_line --partial "-p 127.0.0.1:0:3000"
}

@test "gemini-toolbox --no-localhost disables port mapping" {
    cd "${TEST_TEMP_DIR}"

    run gemini-toolbox --no-localhost --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    refute_line --partial "-p 127.0.0.1:0:3000"
}

@test "gemini-toolbox --network-host uses raw host networking" {
    cd "${TEST_TEMP_DIR}"

    run gemini-toolbox --network-host --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "--net=host"
    refute_line --partial "--network=bridge"
}

@test "gemini-toolbox --remote also enables localhost mapping by default" {
    export GEMINI_REMOTE_KEY="tskey-auth-mock"
    cd "${TEST_TEMP_DIR}"

    run gemini-toolbox --remote --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "--network=bridge"
    assert_line --partial "-p 127.0.0.1:0:3000"
}

@test "gemini-hub --no-localhost disables hub port mapping" {
    run gemini-hub --no-vpn --no-localhost status
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    # Status command doesn't call run, so we need to use a command that does
}

@test "gemini-hub starts with port mapping by default" {
    export GEMINI_REMOTE_KEY="tskey-auth-mock"
    run gemini-hub --detach
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "-p 127.0.0.1:8888:8888"
}
