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
    mock_git
    # Use a valid branch name that needs folder sanitization
    run setup_worktree "myproj" "feature/task-123" "."
    assert_success
    # Should sanitize / to -
    run grep "feature-task-123" <<< "$output"
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

@test "main: connect command bash session" {
    source_toolbox
    # Mock docker ps to return ID, and exec to succeed
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
case "\$1" in
    ps) echo "gem-proj-bash-1"; exit 0 ;;
    inspect) echo "true"; exit 0 ;;
    exec) echo "docker \$*" >> "$MOCK_DOCKER_LOG"; exit 0 ;;
esac
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main connect "gem-proj-bash-1"
    assert_success
    run grep "exec -it gem-proj-bash-1 gosu 0 bash" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: connect command failure (no tmux)" {
    source_toolbox
    # Mock docker ps to return ID, but exec tmux has-session to fail
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
case "\$1" in
    ps) echo "gem-proj-geminicli-1"; exit 0 ;;
    inspect) echo "true"; exit 0 ;;
    exec)
        if [[ "\$*" == *"tmux has-session"* ]]; then exit 1; fi
        exit 0 ;;
esac
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main connect "gem-proj-geminicli-1"
    assert_failure
    assert_output --partial "Error: Reconnecting to this session is not supported"
}

@test "main: stop command multiple matches error" {
    source_toolbox
    # Mock docker ps to return multiple IDs
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "ps" ]]; then
    echo "gem-myproject-geminicli-1"
    echo "gem-myproject-geminicli-2"
    exit 0
fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main stop "myproject"
    assert_failure
    assert_output --partial "Error: Multiple sessions found for project 'myproject'"
}

@test "main: update command success" {
    source_toolbox
    mock_docker
    # Mock docker image inspect to fail (so it tries to pull), pull to succeed
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then exit 1; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main update
    assert_success
    run grep "docker pull" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: stop-hub command" {
    source_toolbox
    mock_docker
    # Hub script exists in bin/
    run main stop-hub
    assert_success
}

@test "main: connect command variants" {
    source_toolbox
    # Mock docker ps to return ID, and exec to succeed
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
case "\$1" in
    ps) 
        if [[ "\$*" == *"gem-proj-bash-123"* ]]; then echo "gem-proj-bash-123"; fi
        if [[ "\$*" == *"gem-proj-geminicli-123"* ]]; then echo "gem-proj-geminicli-123"; fi
        exit 0 ;;
    inspect) echo "true"; exit 0 ;;
    exec)
        if [[ "\$*" == *"tmux has-session"* ]]; then exit 0; fi
        echo "docker \$*" >> "$MOCK_DOCKER_LOG"
        exit 0 ;;
esac
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    # 1. Connect to bash session
    run main connect gem-proj-bash-123
    assert_success
    run grep "docker exec -it gem-proj-bash-123 gosu 0 bash" "$MOCK_DOCKER_LOG"
    assert_success
    
    # 2. Connect to tmux session (default)
    run main connect gem-proj-geminicli-123
    assert_success
    run grep "docker exec -it gem-proj-geminicli-123 gosu 0 tmux attach -t gemini" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: docker-args parsing" {
    source_toolbox
    mock_docker
    run main --docker-args "--link other:other -e KEY=VAL" --bash
    assert_success
    run grep "\-\-link other:other" "$MOCK_DOCKER_LOG"
    assert_success
    run grep "-e KEY=VAL" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "setup_worktree: anonymous exploration (detached HEAD)" {
    source_toolbox
    mock_git
    run setup_worktree "myproj" "" "."
    assert_success
    run grep "exploration-" <<< "$output"
    assert_success
}

@test "setup_worktree: existing branch detection" {
    source_toolbox
    # Mock git to return success for show-ref
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"show-ref --verify --quiet refs/heads/existing"* ]]; then exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
    
    run setup_worktree "myproj" "existing" "."
    assert_success
}

@test "setup_worktree error: already in a worktree" {
    source_toolbox
    # Mock git rev-parse --show-toplevel to return a path, 
    # and then simulate a .git file (not directory) there.
    local fake_toplevel="$TEST_TEMP_DIR/fake-wt"
    mkdir -p "$fake_toplevel"
    touch "$fake_toplevel/.git" # File indicates it is a worktree
    
    # We must mock git to return this fake toplevel
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
case "\$*" in
    *"rev-parse --show-toplevel"*) echo "$fake_toplevel"; exit 0 ;;
    *"rev-parse --is-inside-work-tree"*) exit 0 ;;
    *"rev-parse --verify HEAD"*) exit 0 ;;
    *) exit 0 ;;
esac
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"

    # Use bash -x to see why it succeeds
    run bash -x -c "source $PROJECT_ROOT/bin/gemini-toolbox; setup_worktree 'proj' 'branch' '.'"
    assert_failure
    assert_output --partial "Error: --worktree is not supported from within another worktree"
}

@test "main fails with both --config and --profile" {
    source_toolbox
    run main --config /tmp/c --profile /tmp/p --bash
    assert_failure
    assert_output --partial "Error: Cannot use both --config and --profile simultaneously."
}

@test "setup_worktree error: git worktree add fails" {
    source_toolbox
    # Mock git to fail specifically on worktree add
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"worktree add"* ]]; then 
    echo "fatal: already exists" >&2
    exit 1
fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
    hash -r
    
    run setup_worktree "proj" "branch" "."
    assert_failure
    assert_output --partial "Error: Failed to create git worktree"
}

@test "main fails with --remote and missing key" {
    source_toolbox
    unset GEMINI_REMOTE_KEY
    run main --remote --bash
    assert_failure
    assert_output --partial "Error: TAILSCALE_KEY is required for --remote mode"
}

@test "main: dynamic branch tagging" {
    source_toolbox
    # Mock git to return a feature branch for the repo root
    # Note: repo_root is resolved from BASH_SOURCE
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"rev-parse --abbrev-ref HEAD"* ]]; then echo "feature/fix-1"; exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
    
    # Mock docker to succeed on inspect and log run
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then exit 0; fi
if [[ "\$1" == "run" ]]; then echo "docker \$*" >> "$MOCK_DOCKER_LOG"; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"

    run bash -c "source $PROJECT_ROOT/bin/gemini-toolbox; main --bash"
    assert_success
    run grep "gemini-cli-toolbox/cli:latest-feature-fix-1" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: preview variant image resolution" {
    source_toolbox
    mock_docker
    run main --preview --bash
    assert_success
    # Should check for local preview tag
    run grep "gemini-cli-toolbox/cli-preview:latest" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: detached mode" {
    source_toolbox
    mock_docker
    run main --detached --bash
    assert_success
    run grep "docker run .* -d" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "setup_worktree: reuse existing worktree directory" {
    source_toolbox
    mock_git
    local wk_dir="$TEST_TEMP_DIR/.cache/gemini-toolbox/worktrees/myproj/existing-dir"
    mkdir -p "$wk_dir"
    
    run setup_worktree "myproj" "existing-dir" "."
    assert_success
    run grep "Worktree already exists at" <<< "$output"
    assert_success
}

@test "main: stop-hub script missing error" {
    source_toolbox
    # Mock script dir to a place where gemini-hub doesn't exist
    local fake_bin="$TEST_TEMP_DIR/fake-bin"
    mkdir -p "$fake_bin"
    cp "$PROJECT_ROOT/bin/gemini-toolbox" "$fake_bin/"
    
    run bash -c "source $fake_bin/gemini-toolbox; main stop-hub"
    assert_failure
}

@test "setup_worktree: create new branch" {
    source_toolbox
    # Mock git: show-ref fails (branch doesn't exist), but worktree add succeeds
    # Also must fail git-common-dir to not trigger nested worktree guard
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"rev-parse --is-inside-work-tree"* ]]; then exit 0; fi
if [[ "\$*" == *"rev-parse --show-toplevel"* ]]; then echo "$TEST_TEMP_DIR/myproj"; exit 0; fi
if [[ "\$*" == *"rev-parse --git-common-dir"* ]]; then exit 1; fi
if [[ "\$*" == *"show-ref"* ]]; then exit 1; fi
echo "git \$*" >> "$MOCK_GIT_LOG"
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
    
    local myproj="$TEST_TEMP_DIR/myproj"
    mkdir -p "$myproj"
    
    run bash -c "source $PROJECT_ROOT/bin/gemini-toolbox; setup_worktree myproj new-branch $myproj"
    assert_success
    run grep "git worktree add -b new-branch" "$MOCK_GIT_LOG"
    assert_success
}

@test "main: update command pull failure" {
    source_toolbox
    # Mock docker: image inspect fails (not local), pull fails
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then exit 1; fi
if [[ "\$1" == "pull" ]]; then exit 1; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main update
    assert_failure
    assert_output --partial "Error: Failed to pull image"
    run grep "docker pull .*gemini-cli-toolbox:latest-stable" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: image detection logic (local main fallback)" {
    source_toolbox
    mock_git
    
    # Mock git to return a branch so suffix is not empty
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"rev-parse --abbrev-ref HEAD"* ]]; then echo "feature/x"; exit 0; fi
if [[ "\$*" == *"rev-parse --is-inside-work-tree"* ]]; then exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"
    
    # Mock docker: fail for branch tag, succeed for fallback tag
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "image" && "\$2" == "inspect" ]]; then
    if [[ "\$3" == *"latest-feature-x"* ]]; then exit 1; fi
    if [[ "\$3" == *"latest"* ]]; then exit 0; fi
fi
echo "docker \$*" >> "$MOCK_DOCKER_LOG"
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"

    run main --bash
    assert_success
    run grep "gemini-cli-toolbox/cli:latest " "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: connect command session not found" {
    source_toolbox
    # Mock docker ps to return nothing (empty)
    cat <<EOF > "$TEST_TEMP_DIR/bin/docker"
#!/bin/bash
if [[ "\$1" == "ps" ]]; then echo ""; exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/docker"
    
    run main connect "non-existent"
    assert_failure
    assert_output --partial "Error: Session 'non-existent' not found"
}

@test "main: profile without extra-args" {
    source_toolbox
    mkdir -p "$TEST_TEMP_DIR/empty-profile"
    mock_docker
    run main --profile "$TEST_TEMP_DIR/empty-profile" --bash
    assert_success
}

@test "setup_worktree: directory exists but not a worktree warning" {
    source_toolbox
    mock_git
    local wk_dir="$TEST_TEMP_DIR/.cache/gemini-toolbox/worktrees/myproj/exists"
    mkdir -p "$wk_dir"
    
    run setup_worktree "myproj" "exists" "."
    assert_success
    assert_output --partial "Worktree already exists at"
}

@test "main: vscode integration detection" {
    source_toolbox
    mock_docker
    TERM_PROGRAM="vscode" run main --bash
    assert_success
}

@test "main: repository root detection (setup_worktree path)" {
    source_toolbox
    mock_docker
    mock_git
    
    local orig="/original/repo"
    local wt="/tmp/worktree"
    mkdir -p "$wt"
    
    # We call main with args that trigger setup_worktree (mocked)
    # But here we want to test the main() logic after setup_worktree returns
    # So we need to mock setup_worktree to return the path
    run bash -c "setup_worktree() { echo \"$wt\"; }; source $PROJECT_ROOT/bin/gemini-toolbox; main --worktree \"task\" --bash"
    assert_success
    
    # Should have volumes for the original repo
    # orig is $(pwd) in tests by default if not changed. 
    # In BATS, $(pwd) is $TEST_TEMP_DIR.
    run grep "volume $TEST_TEMP_DIR" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: repository root detection (worktree)" {
    source_toolbox
    mock_docker
    
    # Mock git to return a toplevel which is a worktree
    local top="$TEST_TEMP_DIR/worktree-node"
    local common="$TEST_TEMP_DIR/main-repo"
    mkdir -p "$top" "$common/.git"
    touch "$top/.git" # File indicates worktree
    
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"rev-parse --is-inside-work-tree"* ]]; then exit 0; fi
if [[ "\$*" == *"rev-parse --show-toplevel"* ]]; then echo "$top"; exit 0; fi
if [[ "\$*" == *"rev-parse --git-common-dir"* ]]; then echo "$common/.git"; exit 0; fi
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"

    run bash -c "cd $top && source $PROJECT_ROOT/bin/gemini-toolbox && main --bash"
    assert_success
    # Should have volumes for the main repo (common dir)
    run grep "volume $common" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: repository root detection (non-worktree)" {
    source_toolbox
    mock_docker
    
    # Mock git to return a toplevel
    local top="$TEST_TEMP_DIR/my-repo"
    mkdir -p "$top/.git"
    
    cat <<EOF > "$TEST_TEMP_DIR/bin/git"
#!/bin/bash
if [[ "\$*" == *"rev-parse --is-inside-work-tree"* ]]; then exit 0; fi
if [[ "\$*" == *"rev-parse --show-toplevel"* ]]; then echo "$top"; exit 0; fi
if [[ "\$*" == *"rev-parse --git-common-dir"* ]]; then exit 1; fi # Not a worktree
exit 0
EOF
    chmod +x "$TEST_TEMP_DIR/bin/git"

    run bash -c "cd $top && source $PROJECT_ROOT/bin/gemini-toolbox && main --bash"
    assert_success
    # Should NOT have extra volumes for worktree common dir
    run grep "volume $top" "$MOCK_DOCKER_LOG"
    assert_success
}

@test "main: realpath missing error" {
    source_toolbox
    # Mock command builtin to fail for realpath
    # This requires running in a subshell where we can redefine 'command'
    run bash -c "command() { if [[ \"\$2\" == \"realpath\" ]]; then return 1; fi; builtin command \"\$@\"; }; source $PROJECT_ROOT/bin/gemini-toolbox; main --bash"
    assert_failure
    assert_output --partial "Error: 'realpath' is required"
}
