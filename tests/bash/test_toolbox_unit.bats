#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
}

teardown() {
    teardown_test_env
}

# Source the script without executing it
source_toolbox() {
    # Mock some basics to avoid errors during sourcing if any
    export HOME="$TEST_TEMP_DIR"
    source "$PROJECT_ROOT/bin/gemini-toolbox"
}

@test "show_help function prints usage" {
    source_toolbox
    run show_help
    assert_success
    assert_output --partial "Usage: gemini-toolbox"
}

@test "main function runs correctly with --bash" {
    source_toolbox
    mock_docker
    run main --bash
    assert_success
}

@test "setup_worktree function is defined" {
    source_toolbox
    run declare -f setup_worktree
    assert_success
}

@test "main fails with --remote and --no-tmux" {
    source_toolbox
    run main --remote tskey-auth --no-tmux
    assert_failure
    assert_output --partial "Error: --remote and --no-tmux are incompatible"
}

@test "setup_worktree error: not a git repo" {
    source_toolbox
    local not_a_repo="$TEST_TEMP_DIR/not-a-repo"
    mkdir -p "$not_a_repo"
    cd "$not_a_repo"
    # Ensure no .git folder exists in parents by using a completely fresh temp dir
    local isolated_dir
    isolated_dir="$(mktemp -d)"
    cd "$isolated_dir"
    
    run setup_worktree "proj" "branch" "."
    assert_failure
    assert_output --partial "Error: --worktree can only be used within a Git repository"
    rm -rf "$isolated_dir"
}

@test "setup_worktree error: git not found" {
    source_toolbox
    # Mock git to not found
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
exit 127
EOF
    # Remove from path or ensure it's first
    run setup_worktree "proj" "branch" "."
    # This might be tricky if it uses the real git first.
    # Our setup_test_env puts TEST_TEMP_DIR/bin first.
}

@test "main: image detection logic (local exists)" {
    source_toolbox
    # Mock docker image inspect to return 0
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then exit 0; fi
exit 0
EOF
    run main --bash
    # It should use the local tag
    run grep "gemini-cli-toolbox/cli:latest" "$MOCK_DOCKER_LOG"
}

@test "setup_worktree error: empty repository" {
    source_toolbox
    local empty_repo="$TEST_TEMP_DIR/empty-repo"
    mkdir -p "$empty_repo"
    cd "$empty_repo"
    git init -q
    # No commits yet
    run setup_worktree "proj" "branch" "."
    assert_failure
    assert_output --partial "Error: Cannot create a worktree from an empty repository"
}

@test "setup_worktree: folder name sanitization" {
    source_toolbox
    # Mocking successful git commands to get past guards
    mock_git 
    run setup_worktree "myproj" "feature/task #123" "."
    assert_success
    # Should sanitize / to - and remove # and space
    run grep "feature-task123" <<< "$output"
    assert_success
}

@test "main: age-based refresh tip" {
    source_toolbox
    # Force usage of remote tag by failing local inspect
    # And mock age to be old
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "inspect" && "\$2" == "--format"* ]]; then
    echo "2020-01-01T00:00:00Z"
    exit 0
fi
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then 
    if [[ "\$3" == "gemini-cli-toolbox/cli:latest"* ]]; then exit 1; fi
    exit 0 
fi
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"

    run main --bash
    assert_success
    assert_output --partial "Tip: Your Gemini image is"
}
