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

@test "Journey 3: Config Override (--config)" {
    mkdir -p "$TEST_TEMP_DIR/custom-config"
    run gemini-toolbox --config "$TEST_TEMP_DIR/custom-config" --bash
    assert_success
    run grep "custom-config:/home/gemini/.gemini" "$MOCK_DOCKER_LOG"
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
    # Mock docker to return the ID for ps check
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "ps" ]]; then echo "gem-test-session"; exit 0; fi
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    run gemini-toolbox connect gem-test-session
    assert_success
    run grep "docker exec .* gem-test-session" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 9: Stop - Single Match" {
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

@test "Journey 9: Stop - Multiple Matches (Failure)" {
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == "ps"* ]]; then
    echo "gem-myproject-geminicli-1"
    echo "gem-myproject-geminicli-2"
    exit 0
fi
EOF
    run gemini-toolbox stop myproject
    assert_failure
    assert_output --partial "Error: Multiple sessions found"
}

@test "Journey 9: Stop - No Matches (Failure)" {
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == "ps"* ]]; then
    exit 0
fi
EOF
    run gemini-toolbox stop myproject
    assert_failure
    assert_output --partial "Error: No active sessions found"
}

@test "Journey 10: Update" {
    run gemini-toolbox --image remote/image update
    run grep "docker pull remote/image" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "Journey 10: Update - Local Image (Failure)" {
    run gemini-toolbox update
    assert_failure
    assert_output --partial "Error: You are using a local image"
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
    run grep "gem-worktree-repo-feat-branch-bash" "$MOCK_DOCKER_LOG"
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

@test "Journey: Profile with Extra Args" {
    mkdir -p "$TEST_TEMP_DIR/args-profile"
    echo "--no-docker" > "$TEST_TEMP_DIR/args-profile/extra-args"
    run gemini-toolbox --profile "$TEST_TEMP_DIR/args-profile" --bash
    assert_success
    run grep "/var/run/docker.sock" "$MOCK_DOCKER_LOG"
    assert_failure
}

@test "Journey: Invalid Project Path (Failure)" {
    run gemini-toolbox --project /non/existent/path
    assert_failure
    assert_output --partial "Error: Project directory"
}

@test "Journey: Simultaneous Config and Profile (Failure)" {
    run gemini-toolbox --config /tmp/c --profile /tmp/p
    assert_failure
    assert_output --partial "Error: Cannot use both --config and --profile"
}

@test "Journey: Environment Propagation" {
    # Using a simple test case to avoid any side effects
    HTTP_PROXY="http://proxy:8080" COLORTERM="truecolor" LANG="en_US.UTF-8" run gemini-toolbox --bash
    assert_success
    
    run grep "ENV: HTTP_PROXY=http://proxy:8080" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "ENV: COLORTERM=truecolor" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "ENV: LANG=en_US.UTF-8" "$MOCK_DOCKER_LOG"
    assert_success
}
