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
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/tailscale"
#!/bin/bash
echo "tailscale \$*" >> "$MOCK_GIT_LOG"
EOF
    cat <<EOF > "$TEST_TEMP_DIR/bin/python"
#!/bin/bash
echo "python \$*" >> "$MOCK_GIT_LOG"
EOF
    chmod +x "$TEST_TEMP_DIR/bin/"*
}

@test "Hub Entrypoint: authentication and startup" {
    mock_hub_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_hub.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
export TAILSCALE_AUTH_KEY="tskey-hub-123"
source "\$PROJECT_ROOT/images/gemini-hub/docker-entrypoint.sh"
main
EOF
    chmod +x "$TEST_TEMP_DIR/run_hub.sh"
    
    run "$TEST_TEMP_DIR/run_hub.sh"
    assert_success
    run grep "tailscale up --authkey=tskey-hub-123 --hostname=gemini-hub --force-reauth" "$MOCK_GIT_LOG"
    assert_success
    run grep "python run.py" "$MOCK_GIT_LOG"
    assert_success
}

@test "Hub Entrypoint: error on missing key" {
    mock_hub_commands
    
    cat <<EOF > "$TEST_TEMP_DIR/run_hub.sh"
#!/bin/bash
export PROJECT_ROOT=$PROJECT_ROOT
unset TAILSCALE_AUTH_KEY
source "\$PROJECT_ROOT/images/gemini-hub/docker-entrypoint.sh"
main
EOF
    chmod +x "$TEST_TEMP_DIR/run_hub.sh"
    
    run "$TEST_TEMP_DIR/run_hub.sh"
    assert_failure
    assert_output --partial "Error: TAILSCALE_AUTH_KEY is missing"
}
