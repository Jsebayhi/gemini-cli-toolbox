_gemini_toolbox_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="update stop-hub stop connect"
    opts="--preview --image --no-ide --no-docker --config --profile --project --remote --docker-args --volume --worktree --name --bash --no-tmux --detached --help -v"

    case "${prev}" in
        --config)
            # Directory completion only (no guessing)
            COMPREPLY=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        --project)
            # Directory completion
            COMPREPLY=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        --profile)
            # Suggest absolute paths from standard profile locations
            local xdg_conf_home="${XDG_CONFIG_HOME:-$HOME/.config}"
            local search_dirs=(
                "${xdg_conf_home}/gemini-toolbox/profiles"
                "${HOME}/.gemini-profiles"
            )
            local profiles=""
            for dir in "${search_dirs[@]}"; do
                if [ -d "$dir" ]; then
                    # Get full absolute paths
                    for p in "${dir}"/*; do
                        if [ -d "$p" ]; then
                            profiles="${profiles} ${p}"
                        fi
                    done
                fi
            done
            COMPREPLY=( $(compgen -W "${profiles}" -- "${cur}") )
            # Always allow local directory completion
            COMPREPLY+=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        --image)
            # Suggest local gemini-cli-toolbox images
            if command -v docker >/dev/null 2>&1; then
                local images
                images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "gemini-cli-toolbox" | grep -v "hub")
                COMPREPLY=( $(compgen -W "${images}" -- "${cur}") )
            fi
            return 0
            ;;
        --volume|-v)
            # File/Directory completion
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
        --name)
            # Suggest existing worktrees for the current project
            local project_name
            project_name=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
            local worktree_base="${GEMINI_WORKTREE_ROOT:-${XDG_CACHE_HOME:-$HOME/.cache}/gemini-toolbox/worktrees/${project_name}}"
            if [ -d "$worktree_base" ]; then
                COMPREPLY=( $(compgen -W "$(ls "${worktree_base}")" -- "${cur}") )
            fi
            return 0
            ;;
        connect)
            # Complete running gemini container IDs (full names)
            if command -v docker >/dev/null 2>&1; then
                local running_containers
                running_containers=$(docker ps --format "{{.Names}}" --filter "name=gem-" 2>/dev/null)
                COMPREPLY=( $(compgen -W "${running_containers}" -- "${cur}") )
            fi
            return 0
            ;;
        stop)
            # Complete running gemini container IDs AND project names extracted from them
            if command -v docker >/dev/null 2>&1; then
                local names
                names=$(docker ps --format "{{.Names}}" --filter "name=gem-" 2>/dev/null)
                # Extract PROJECT from gem-{PROJECT}-{TYPE}-{ID}
                local projects
                projects=$(echo "$names" | sed 's/^gem-//; s/-[^-]*-[^-]*$//' | sort -u)
                COMPREPLY=( $(compgen -W "${names} ${projects}" -- "${cur}") )
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
