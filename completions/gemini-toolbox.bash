_gemini_toolbox_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="update stop-hub connect"
    opts="--preview --no-ide --no-docker --config --profile --project --remote --docker-args --volume --bash --detached --help -v"

    case "${prev}" in
        --config|--profile|--project)
            # Directory completion
            COMPREPLY=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        --volume|-v)
            # File/Directory completion
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
        connect)
            # Complete running gemini container names if docker is available
            if command -v docker >/dev/null 2>&1; then
                local running_containers=$(docker ps --format "{{.Names}}" --filter "name=gem-" 2>/dev/null)
                COMPREPLY=( $(compgen -W "${running_containers}" -- "${cur}") )
            fi
            return 0
            ;;
    esac

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    fi

    COMPREPLY=( $(compgen -W "${commands} ${opts}" -- "${cur}") )
}

complete -F _gemini_toolbox_completions gemini-toolbox
