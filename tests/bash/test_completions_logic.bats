#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    # Source the completion script
    source "$PROJECT_ROOT/completions/gemini-toolbox.bash"
}

@test "gemini-toolbox: --name only suggests from worktree cache" {
    # Mock COMP_WORDS and COMP_CWORD
    # gemini-toolbox --name 
    COMP_WORDS=(gemini-toolbox --name "")
    COMP_CWORD=2
    COMPREPLY=()
    
    # We create some local project directories that should NOT be suggested
    mkdir -p local_subdir1 local_subdir2
    
    # setup_test_env sets HOME to TEST_TEMP_DIR
    local project_name
    project_name=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
    local worktree_base="$HOME/.cache/gemini-toolbox/worktrees/${project_name}"
    mkdir -p "$worktree_base/existing-wt"
    
    _gemini_toolbox_completions
    
    # Check if existing-wt is in COMPREPLY
    local found=false
    for reply in "${COMPREPLY[@]}"; do
        if [ "$reply" == "existing-wt" ]; then
            found=true
        fi
        # COMPREPLY should NOT contain local subdirs
        [ "$reply" != "local_subdir1" ]
        [ "$reply" != "local_subdir2" ]
    done
    [ "$found" == "true" ]
}

@test "gemini-toolbox: --name respects custom GEMINI_WORKTREE_ROOT" {
    # Mock COMP_WORDS and COMP_CWORD
    # gemini-toolbox --name 
    COMP_WORDS=(gemini-toolbox --name "")
    COMP_CWORD=2
    COMPREPLY=()
    
    # Set a custom worktree root
    export GEMINI_WORKTREE_ROOT="$TEST_TEMP_DIR/custom-wt-root"
    local project_name
    project_name=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
    local worktree_base="${GEMINI_WORKTREE_ROOT}/${project_name}"
    mkdir -p "$worktree_base/custom-root-wt"
    
    _gemini_toolbox_completions
    
    # Check if custom-root-wt is in COMPREPLY
    local found=false
    for reply in "${COMPREPLY[@]}"; do
        if [ "$reply" == "custom-root-wt" ]; then
            found=true
        fi
    done
    [ "$found" == "true" ]
}

@test "gemini-toolbox: --name respects --project flag" {
    # Mock COMP_WORDS and COMP_CWORD
    # gemini-toolbox --project /other/path --name 
    COMP_WORDS=(gemini-toolbox --project "/other/path" --name "")
    COMP_CWORD=4
    COMPREPLY=()
    
    # Cache for "/other/path"
    local project_name="path"
    local worktree_base="$HOME/.cache/gemini-toolbox/worktrees/${project_name}"
    mkdir -p "$worktree_base/other-project-wt"
    
    _gemini_toolbox_completions
    
    # Check if other-project-wt is in COMPREPLY
    local found=false
    for reply in "${COMPREPLY[@]}"; do
        if [ "$reply" == "other-project-wt" ]; then
            found=true
        fi
    done
    [ "$found" == "true" ]
}

@test "gemini-toolbox: --name correctly sanitizes project name" {
    # Mock COMP_WORDS and COMP_CWORD
    # gemini-toolbox --project "/path/My Project!" --name 
    COMP_WORDS=(gemini-toolbox --project "/path/My Project!" --name "")
    COMP_CWORD=4
    COMPREPLY=()
    
    # Expected sanitized project name: "my-project-"
    local sanitized_name="my-project-"
    local worktree_base="$HOME/.cache/gemini-toolbox/worktrees/${sanitized_name}"
    mkdir -p "$worktree_base/sanitized-project-wt"
    
    _gemini_toolbox_completions
    
    # Check if sanitized-project-wt is in COMPREPLY
    local found=false
    for reply in "${COMPREPLY[@]}"; do
        if [ "$reply" == "sanitized-project-wt" ]; then
            found=true
        fi
    done
    [ "$found" == "true" ]
}
