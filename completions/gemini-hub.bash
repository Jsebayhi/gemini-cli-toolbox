_gemini_hub_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="stop"
    opts="--detach -d --image --key --auto-shutdown --no-worktree-prune --workspace --config-root --help -h"

    case "${prev}" in
        --workspace)
            # Directory completion
            COMPREPLY=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        --config-root)
            # Suggest absolute paths from standard profile locations
            local xdg_conf_home="${XDG_CONFIG_HOME:-$HOME/.config}"
            local search_dirs=(
                "${xdg_conf_home}/gemini-toolbox/profiles"
                "${HOME}/.gemini-profiles"
            )
            local paths=""
            for dir in "${search_dirs[@]}"; do
                if [ -d "$dir" ]; then
                    paths="${paths} ${dir}"
                fi
            done
            COMPREPLY=( $(compgen -W "${paths}" -- "${cur}") )
            # Also allow any directory
            COMPREPLY+=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        --image)
            # Suggest local gemini-cli-toolbox hub images
            if command -v docker >/dev/null 2>&1; then
                local images
                images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "gemini-cli-toolbox/hub")
                COMPREPLY=( $(compgen -W "${images}" -- "${cur}") )
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

complete -F _gemini_hub_completions gemini-hub
