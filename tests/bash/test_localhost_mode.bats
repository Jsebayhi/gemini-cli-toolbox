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

@test "gemini-toolbox --remote launches vpn sidecar" {
    export GEMINI_REMOTE_KEY="tskey-auth-mock"
    cd "${TEST_TEMP_DIR}"

    run gemini-toolbox --remote --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    # 1. Check parent started
    assert_line --partial "run --rm -d --name gem-"
    # 2. Check sidecar started with shared namespaces
    assert_line --partial "run --rm -d --name gem-"
    assert_line --partial "-vpn"
    assert_line --partial "--network container:gem-"
    assert_line --partial "--pid container:gem-"
    assert_line --partial "com.gemini.role=sidecar"
    assert_line --partial "TAILSCALE_AUTH_KEY=tskey-auth-mock"
}

@test "gemini-toolbox vpn-add attaches sidecar to existing session" {
    export GEMINI_REMOTE_KEY="tskey-auth-mock"
    
    # Mock a running session
    cat <<EOF > "${TEST_TEMP_DIR}/docker_ps.out"
gem-project-cli-123
EOF
    function docker() {
        if [[ "$*" == "ps"* ]]; then cat "${TEST_TEMP_DIR}/docker_ps.out"; return 0; fi
        echo "DOCKER_CALL: $*" >> "${MOCK_DOCKER_LOG}"
    }
    export -f docker

    run gemini-toolbox vpn-add gem-project-cli-123
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "run --rm -d --name gem-project-cli-123-vpn"
    assert_line --partial "--network container:gem-project-cli-123"
}

@test "gemini-toolbox lan-add attaches sidecar to existing session" {
    # Mock a running session
    cat <<EOF > "${TEST_TEMP_DIR}/docker_ps.out"
gem-project-cli-123
EOF
    function docker() {
        if [[ "$*" == "ps"* ]]; then cat "${TEST_TEMP_DIR}/docker_ps.out"; return 0; fi
        echo "DOCKER_CALL: $*" >> "${MOCK_DOCKER_LOG}"
    }
    export -f docker

    run gemini-toolbox lan-add gem-project-cli-123
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "run --rm -d --name gem-project-cli-123-lan"
    assert_line --partial "-p 0.0.0.0:3000:3000"
}

@test "gemini-hub --detach launches vpn sidecar if key provided" {
    export GEMINI_REMOTE_KEY="tskey-auth-mock"
    
    run gemini-hub --detach
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    # Hub itself
    assert_line --partial "run --rm -d --name gemini-hub-service"
    # Hub VPN Sidecar
    assert_line --partial "run --rm -d --name gemini-hub-service-vpn"
}
