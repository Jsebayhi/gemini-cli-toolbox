#!/usr/bin/env bats

load "libs/bats-support/load"
load "libs/bats-assert/load"

setup() {
    export TEST_TEMP_DIR="$(mktemp -d)"
    export MOCK_DOCKER_LOG="${TEST_TEMP_DIR}/docker.log"
    touch "${MOCK_DOCKER_LOG}"
    
    # Fake realpath if missing
    if ! command -v realpath >/dev/null 2>&1; then
        function realpath() { echo "$1"; }
        export -f realpath
    fi

    function docker() {
        echo "DOCKER_CALL: $*" >> "${MOCK_DOCKER_LOG}"
        if [[ "$*" == "inspect --format"* ]]; then
            echo "32768"
            return 0
        fi
        return 0
    }
    export -f docker

    # Add bin to path
    export PATH="${BATS_TEST_DIRNAME}/../../bin:${PATH}"
    
    # Mock home
    export HOME="${TEST_TEMP_DIR}/home"
    mkdir -p "${HOME}"
}

teardown() {
    rm -rf "${TEST_TEMP_DIR}"
}

@test "gemini-toolbox --no-vpn uses bridge network and maps port" {
    cd "${TEST_TEMP_DIR}"
    run gemini-toolbox --no-vpn --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "run --rm -d --name gem-tmp-"
    assert_line --partial "--network=bridge"
    assert_line --partial "-p 127.0.0.1:0:3000"
}

@test "gemini-toolbox defaults to protected localhost (bridge + mapping)" {
    cd "${TEST_TEMP_DIR}"
    run gemini-toolbox --detached --image busybox -- -c "ls"
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
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
    refute_line --partial "-p 127.0.0.1:0:3000"
}

@test "gemini-hub --no-vpn uses bridge network and maps port" {
    run gemini-hub --no-vpn --detach --image busybox
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    assert_line --partial "run --rm -d --name gemini-hub-service"
    assert_line --partial "--network=bridge"
    assert_line --partial "-p 127.0.0.1:8888:8888"
}

@test "gemini-hub --no-localhost disables port mapping" {
    run gemini-hub --no-vpn --no-localhost --detach --image busybox
    
    assert_success
    run cat "${MOCK_DOCKER_LOG}"
    refute_line --partial "-p 127.0.0.1:8888:8888"
}
