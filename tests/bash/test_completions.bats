#!/usr/bin/env bats

load 'test_helper'

setup() {
    setup_test_env
}

@test "gemini-toolbox completion registration" {
    source "$PROJECT_ROOT/completions/gemini-toolbox.bash"
    run complete -p gemini-toolbox
    assert_success
    assert_output "complete -F _gemini_toolbox_completions gemini-toolbox"
}

@test "gemini-toolbox alias completion registration" {
    # Enable alias expansion for the shell running the test
    shopt -s expand_aliases
    alias gt='gemini-toolbox'
    alias gtp='gemini-toolbox --preview'
    
    # Source completion - it should find the alias
    source "$PROJECT_ROOT/completions/gemini-toolbox.bash"
    
    run complete -p gt
    assert_success
    assert_output "complete -F _gemini_toolbox_completions gt"

    run complete -p gtp
    assert_success
    assert_output "complete -F _gemini_toolbox_completions gtp"
}

@test "gemini-hub completion registration" {
    source "$PROJECT_ROOT/completions/gemini-hub.bash"
    run complete -p gemini-hub
    assert_success
    assert_output "complete -F _gemini_hub_completions gemini-hub"
}

@test "gemini-hub alias completion registration" {
    shopt -s expand_aliases
    alias gh='gemini-hub'
    alias ghd='gemini-hub --detach'
    
    source "$PROJECT_ROOT/completions/gemini-hub.bash"
    
    run complete -p gh
    assert_success
    assert_output "complete -F _gemini_hub_completions gh"

    run complete -p ghd
    assert_success
    assert_output "complete -F _gemini_hub_completions ghd"
}
