_gemini_hub_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="stop"
    opts="--detach -d --image --key --auto-shutdown --no-worktree-prune --workspace --config-root --help -h"

    case "${prev}" in
        --workspace|--config-root)
            # Directory completion
            COMPREPLY=( $(compgen -d -- "${cur}") )
            return 0
            ;;
    esac

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    fi

    COMPREPLY=( $(compgen -W "${commands} ${opts}" -- "${cur}") )
}

complete -F _gemini_hub_completions gemini-hub
