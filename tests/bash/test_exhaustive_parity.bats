#!/usr/bin/env bats

load 'test_helper'

# Helper to capture and clean the docker run/stop/pull/ps/exec command for comparison
# We ignore the random UUID suffix which changes every run
capture_cmd() {
    local script="$1"
    shift
    rm -f "$TEST_TEMP_DIR/docker_calls.log"
    # We use a subshell to avoid exit from 'exec' in scripts
    ( run "$script" "$@" ) >/dev/null 2>&1 || true
    
    if [ ! -f "$TEST_TEMP_DIR/docker_calls.log" ]; then
        echo "NO_DOCKER_CALL"
        return
    fi

    # Sanitize:
    # 1. Replace UUIDs in container names/hostnames
    # 2. Replace absolute paths to the test temp dir
    # 3. Replace the current directory path (which might differ slightly)
    cat "$TEST_TEMP_DIR/docker_calls.log" | \
        sed -E 's/gem-[a-zA-Z0-9-]+-[a-z0-9-]+-[a-z0-9]{8}/gem-snapshot-mock/g' | \
        sed "s|$TEST_TEMP_DIR|TEST_TEMP_DIR_MOCK|g" | \
        sed "s|$(pwd)|CWD_MOCK|g"
}

setup() {
    setup_test_env
    mock_docker
    # Note: Journey 14/17 parity tests will mock real git as needed inside the test
    export TOOLBOX_MAIN="$PROJECT_ROOT/bin/gemini-toolbox.main"
    export TOOLBOX_FEAT="$PROJECT_ROOT/bin/gemini-toolbox"
}

teardown() {
    teardown_test_env
}

@test "Parity: Basic Chat (Default)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN")
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT")
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 1 Parity: Remote Access (--remote)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --remote tskey-auth-123 --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --remote tskey-auth-123 --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 2 Parity: Profiles (--profile)" {
    mkdir -p "$TEST_TEMP_DIR/work-profile"
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --profile "$TEST_TEMP_DIR/work-profile" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --profile "$TEST_TEMP_DIR/work-profile" --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 4 Parity: Sandbox (--no-docker --no-ide)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --no-docker --no-ide --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --no-docker --no-ide --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 6 Parity: Bash One-Liner (-c)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --bash -c "ls -la")
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --bash -c "ls -la")
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 7 Parity: Legacy Config (--config)" {
    mkdir -p "$TEST_TEMP_DIR/legacy"
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --config "$TEST_TEMP_DIR/legacy" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --config "$TEST_TEMP_DIR/legacy" --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 8 Parity: Connect" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" connect gem-test-session)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" connect gem-test-session)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 9 Parity: Stop" {
    # Mocking docker ps to return a matching session
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$*" == "ps"* ]]; then
    echo "gem-myproject-geminicli-abc12345"
    exit 0
fi
echo "docker \$*" >> "$TEST_TEMP_DIR/docker_calls.log"
EOF
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" stop myproject)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" stop myproject)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 10 Parity: Update" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" update)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" update)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 11 Parity: Volume Mounts (-v)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" -v "/src:/dest" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" -v "/src:/dest" --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 12 Parity: VS Code Integration (ENV)" {
    export TERM_PROGRAM="vscode"
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --bash)
    unset TERM_PROGRAM
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 14 Parity: Named Worktree (--worktree --name)" {
    local repo="$TEST_TEMP_DIR/worktree-repo"
    mkdir -p "$repo"
    cd "$repo"
    git init -q
    git config user.email "t@e.com"
    git config user.name "T"
    git commit -q --allow-empty -m "init"
    
    # We must run from inside the repo
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --worktree --name "feat-branch" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --worktree --name "feat-branch" --bash)
    
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Journey 17 Parity: Worktree Parent Detection" {
    local repo="$TEST_TEMP_DIR/j17-repo"
    mkdir -p "$repo"
    cd "$repo"
    git init -q
    git config user.email "t@e.com"
    git config user.name "T"
    git commit -q --allow-empty -m "init"
    
    # Create a real worktree
    local wt_path="$TEST_TEMP_DIR/j17-wt"
    git worktree add "$wt_path" -b "new-branch"
    
    cd "$wt_path"
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --bash)
    
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Parity: Detached Mode (--detached)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --detached --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --detached --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Parity: Preview Image (--preview)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --preview --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --preview --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Parity: Custom Image (--image) - Refactor Fixes Bug in Main" {
    # Note: The original script in 'main' had a bug where --image was overwritten by defaults.
    # Our refactor fixes this. We verify the command contains the custom image.
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --image my-custom-img --bash)
    run echo "$cmd_feat"
    assert_output --partial "'my-custom-img'"
}

@test "Parity: Extra Docker Args (--docker-args)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --docker-args "--label=test --privileged" --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --docker-args "--label=test --privileged" --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Parity: No TMUX (--no-tmux)" {
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --no-tmux --bash)
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --no-tmux --bash)
    [ "$cmd_main" == "$cmd_feat" ]
}

@test "Parity: Combined Stress Test" {
    mkdir -p "$TEST_TEMP_DIR/stress-profile"
    local cmd_main=$(capture_cmd "$TOOLBOX_MAIN" --preview --no-docker --profile "$TEST_TEMP_DIR/stress-profile" -v "/a:/b" --bash -c "ls")
    local cmd_feat=$(capture_cmd "$TOOLBOX_FEAT" --preview --no-docker --profile "$TEST_TEMP_DIR/stress-profile" -v "/a:/b" --bash -c "ls")
    [ "$cmd_main" == "$cmd_feat" ]
}
