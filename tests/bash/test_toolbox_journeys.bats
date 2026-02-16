#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    mock_docker
}

teardown() {
    teardown_test_env
}

@test "Journey: Basic Chat (Default)" {
    run gemini-toolbox chat
    assert_success
    run grep "docker run .* gemini-cli-toolbox/cli:latest" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 1: Remote Access (--remote)" {
    run gemini-toolbox --remote tskey-auth-123 --bash
    assert_success
    run grep "TAILSCALE_AUTH_KEY=tskey-auth-123" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "\-\-network=bridge" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 2: Profiles (--profile)" {
    mkdir -p "$TEST_TEMP_DIR/work-profile"
    run gemini-toolbox --profile "$TEST_TEMP_DIR/work-profile" --bash
    assert_success
    run grep "work-profile/.gemini:/home/gemini/.gemini" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 4: Sandbox (--no-docker --no-ide)" {
    run gemini-toolbox --no-docker --no-ide --bash
    assert_success
    run grep "/var/run/docker.sock" "$MOCK_DOCKER_LOG"
    assert_failure
}

@test "Journey 6: Bash One-Liner (-c)" {
    run gemini-toolbox --bash -c "ls -la"
    assert_success
    run grep "bash -c ls -la" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 8: Connect" {
    run gemini-toolbox connect gem-test-session
    assert_success
    run grep "docker exec .* gem-test-session" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 9: Stop" {
    # Mocking docker ps to return a matching session
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == "ps"* ]]; then
    echo "gem-myproject-geminicli-abc12345"
    exit 0
fi
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
EOF
    run gemini-toolbox stop myproject
    assert_success
    run grep "docker stop gem-myproject-geminicli-abc12345" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 10: Update" {
    run gemini-toolbox --image remote/image update
    run grep "docker pull remote/image" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 11: Volume Mounts (-v)" {
    run gemini-toolbox -v "/src:/dest" --bash
    assert_success
    run grep "\-\-volume /src:/dest" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 14: Named Worktree (--worktree --name)" {
    # Initialize a clean repo for worktree testing
    local repo="$TEST_TEMP_DIR/worktree-repo"
    mkdir -p "$repo"
    cd "$repo"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"
    git commit -q --allow-empty -m "Initial commit"

    run gemini-toolbox --worktree --name "feat-branch" --bash
    assert_success
    run grep "gem-feat-branch-bash" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey: Preview Image (--preview)" {
    run gemini-toolbox --preview --bash
    assert_success
    run grep "gemini-cli-toolbox/cli-preview:latest" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey: Custom Image (--image)" {
    run gemini-toolbox --image custom --bash
    assert_success
    run grep "docker run .* custom" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey: No TMUX (--no-tmux)" {
    run gemini-toolbox --no-tmux --bash
    assert_success
    run grep "GEMINI_TOOLBOX_TMUX=false" "$MOCK_DOCKER_LOG"
    assert_success
}
