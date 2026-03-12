#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
    # Source the completion script
    source "$PROJECT_ROOT/completions/gemini-toolbox.bash"
}

@test "gemini-toolbox: --name suggests directories when --worktree is present" {
    # Mock COMP_WORDS and COMP_CWORD
    # gemini-toolbox --worktree --name 
    COMP_WORDS=(gemini-toolbox --worktree --name "")
    COMP_CWORD=3
    COMPREPLY=()
    
    # We need to be in a directory with some subdirectories
    mkdir -p subdir1 subdir2
    
    _gemini_toolbox_completions
    
    # Check if subdir1 and subdir2 are in COMPREPLY
    # Use grep to find them since COMPREPLY might have other things
    echo "${COMPREPLY[@]}" | grep -q "subdir1"
    echo "${COMPREPLY[@]}" | grep -q "subdir2"
}

@test "gemini-toolbox: --name does not suggest directories when --worktree is absent" {
    # Mock COMP_WORDS and COMP_CWORD
    # gemini-toolbox --name 
    COMP_WORDS=(gemini-toolbox --name "")
    COMP_CWORD=2
    COMPREPLY=()
    
    mkdir -p subdir1 subdir2
    
    _gemini_toolbox_completions
    
    # COMPREPLY should NOT contain subdir1/subdir2 (unless they are existing worktrees, which they aren't here)
    for reply in "${COMPREPLY[@]}"; do
        [ "$reply" != "subdir1" ]
        [ "$reply" != "subdir2" ]
    done
}
