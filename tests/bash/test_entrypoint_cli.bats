#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
}

teardown() {
    teardown_test_env
}

source_entrypoint() {
    export HOME="$TEST_TEMP_DIR"
    source "$PROJECT_ROOT/images/gemini-cli/docker-entrypoint.sh"
}

# Mock system-level commands that entrypoint uses
mock_system_commands() {
    cat <<EOF > "$TEST_TEMP_DIR/bin/hostname"
#!/bin/bash
echo "testhost"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/groupadd"
#!/bin/bash
echo "groupadd \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/useradd"
#!/bin/bash
echo "useradd \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/usermod"
#!/bin/bash
echo "usermod \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/chown"
#!/bin/bash
echo "chown \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/getent"
#!/bin/bash
if [[ "\$1" == "passwd" ]]; then echo "gemini:x:1000:1000::/home/gemini:/bin/bash"; exit 0; fi
if [[ "\$1" == "group" ]]; then exit 1; fi # Force group creation
exit 0
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/gosu"
#!/bin/bash
shift 1 # skip user
if [[ "\$1" == "tmux" && "\$2" == "attach" ]]; then echo "tmux attached"; exit 0; fi
echo "executing: \$*"
exec "\$@"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/tmux"
#!/bin/bash
if [[ "\$1" == "has-session" ]]; then exit 1; fi # End the loop immediately
echo "tmux \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/tailscaled"
#!/bin/bash
echo "tailscaled started"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/tailscale"
#!/bin/bash
echo "tailscale \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/ttyd"
#!/bin/bash
echo "ttyd started"
EOF
    chmod +x "$TEST_TEMP_DIR/bin/"*
}

@test "CLI Entrypoint: basic user creation and permission fixing" {
    mock_system_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_entrypoint.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export TEST_TEMP_DIR=$TEST_TEMP_DIR
export GEMINI_TOOLBOX_TMUX=false
export DEFAULT_UID=1000
export DEFAULT_GID=1000
export DEFAULT_HOME_DIR="$TEST_TEMP_DIR/home"
source "\$PROJECT_ROOT/images/gemini-cli/docker-entrypoint.sh"
main bash --version
EOF
    chmod +x "$TEST_TEMP_DIR/run_entrypoint.sh"
    
    run "$TEST_TEMP_DIR/run_entrypoint.sh"
    [ "$status" -eq 0 ] || echo "$output" >&2
    assert_success
    
    run grep "groupadd -g 1000 gemini" "$MOCK_GIT_LOG"
    assert_success
    run grep "chown -R 1000:1000 $TEST_TEMP_DIR/home" "$MOCK_GIT_LOG"
    assert_success
}

@test "CLI Entrypoint: DooD permission setup" {
    mock_system_commands
    
    # Simulate existing docker socket using python (mkfifo doesn't pass [ -S ])
    python3 -c "import socket, os; s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.bind('$TEST_TEMP_DIR/docker.sock')"
    
    cat <<EOF > "$TEST_TEMP_DIR/run_entrypoint.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export TEST_TEMP_DIR=$TEST_TEMP_DIR
export GEMINI_TOOLBOX_TMUX=false
export HOST_DOCKER_GID=999
export DOCKER_SOCK="$TEST_TEMP_DIR/docker.sock"
export DEFAULT_UID=1000
export DEFAULT_GID=1000
export DEFAULT_HOME_DIR="$TEST_TEMP_DIR/home"
source "\$PROJECT_ROOT/images/gemini-cli/docker-entrypoint.sh"
main bash --version
EOF
    chmod +x "$TEST_TEMP_DIR/run_entrypoint.sh"

    run "$TEST_TEMP_DIR/run_entrypoint.sh"
    [ "$status" -eq 0 ] || echo "$output" >&2
    assert_success
    run grep "groupadd -g 999 host-docker" "$MOCK_GIT_LOG"
    assert_success
    run grep "usermod -aG 999 gemini" "$MOCK_GIT_LOG"
    assert_success
}

@test "CLI Entrypoint: Tmux and Remote mode initialization" {
    mock_system_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_entrypoint.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export TEST_TEMP_DIR=$TEST_TEMP_DIR
export TAILSCALE_AUTH_KEY=tskey-123
export GEMINI_SESSION_ID=gem-test-chat-abc
export DEFAULT_UID=1000
export DEFAULT_GID=1000
export DEFAULT_HOME_DIR="$TEST_TEMP_DIR/home"
source "\$PROJECT_ROOT/images/gemini-cli/docker-entrypoint.sh"
main bash --version
EOF
    chmod +x "$TEST_TEMP_DIR/run_entrypoint.sh"

    run "$TEST_TEMP_DIR/run_entrypoint.sh"
    [ "$status" -eq 0 ] || echo "$output" >&2
    assert_success
    run grep "tailscale up --authkey=tskey-123 --hostname=gem-test-chat-abc" "$MOCK_GIT_LOG"
    assert_success
}

@test "CLI Entrypoint: debug mode and hostname fallback" {
    mock_system_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_entrypoint.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export TAILSCALE_AUTH_KEY=tskey-123
export GEMINI_PROJECT_NAME="my-proj"
export GEMINI_SESSION_TYPE="chat"
export DEFAULT_HOME_DIR="$TEST_TEMP_DIR/home"
source "\$PROJECT_ROOT/images/gemini-cli/docker-entrypoint.sh"
main bash --version
EOF
    chmod +x "$TEST_TEMP_DIR/run_entrypoint.sh"

    run "$TEST_TEMP_DIR/run_entrypoint.sh"
    assert_success
    run grep "tailscale up --authkey=tskey-123 --hostname=gem-my-proj-chat-test" "$MOCK_GIT_LOG"
    assert_success
}

@test "CLI Entrypoint: no-tmux mode explicitly" {
    mock_system_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_entrypoint.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export GEMINI_TOOLBOX_TMUX=false
export DEFAULT_HOME_DIR="$TEST_TEMP_DIR/home"
source "\$PROJECT_ROOT/images/gemini-cli/docker-entrypoint.sh"
main bash --version
EOF
    chmod +x "$TEST_TEMP_DIR/run_entrypoint.sh"

    run "$TEST_TEMP_DIR/run_entrypoint.sh"
    assert_success
    run grep "executing: bash --version" <<< "$output"
    assert_success
}
