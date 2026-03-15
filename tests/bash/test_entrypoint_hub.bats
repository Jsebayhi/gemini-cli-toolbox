#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
}

teardown() {
    teardown_test_env
}

source_entrypoint() {
    source "$PROJECT_ROOT/images/gemini-hub/docker-entrypoint.sh"
}

mock_hub_commands() {
    cat <<EOF > "$TEST_TEMP_DIR/bin/tailscaled"
#!/bin/bash
echo "tailscaled started"
mkdir -p /run/tailscale
touch /run/tailscale/tailscaled.sock
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/tailscale"
#!/bin/bash
echo "tailscale \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/groupadd"
#!/bin/bash
echo "groupadd \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/useradd"
#!/bin/bash
echo "useradd \$*" >> "$MOCK_GIT_LOG"
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
echo "executing as user: \$*"
exec "\$@"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/python"
#!/bin/bash
echo "python \$*" >> "$MOCK_GIT_LOG"
EOF
    chmod +x "$TEST_TEMP_DIR/bin/"*
}

@test "Hub Entrypoint: startup and user creation" {
    mock_hub_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_hub.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export HOST_UID=1000
export HOST_GID=1000
export HOST_DOCKER_GID=999
# Simulate existing docker socket
touch "$TEST_TEMP_DIR/docker.sock"
export DOCKER_SOCK="$TEST_TEMP_DIR/docker.sock"
source "\$PROJECT_ROOT/images/gemini-hub/docker-entrypoint.sh"
main
EOF
    chmod +x "$TEST_TEMP_DIR/run_hub.sh"
    
    run "$TEST_TEMP_DIR/run_hub.sh"
    assert_success
    run grep "groupadd -g 1000 gemini" "$MOCK_GIT_LOG"
    assert_success
    run grep "python run.py" "$MOCK_GIT_LOG"
    assert_success
}

