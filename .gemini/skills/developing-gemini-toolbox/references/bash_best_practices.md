# Bash Best Practices

## 1. Safety & Robustness
*   **Strict Mode:** All scripts MUST start with `set -euo pipefail`.
    *   `-e`: Exit immediately if a command exits with a non-zero status.
    *   `-u`: Treat unset variables as an error.
    *   `-o pipefail`: Return the exit status of the last command in the pipe that failed.
*   **Variable Quoting:** ALWAYS quote variables (`"$VAR"`) to prevent word splitting and globbing, unless you explicitly want that behavior.

## 2. Structure & Modularity
*   **Main Function Pattern:** Wrap the execution logic in a `main` function and call it only if the script is run directly. This allows the script to be `source`d for testing.
    ```bash
    main() {
        # ... logic ...
    }

    if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
        main "$@"
    fi
    ```
*   **Functions:** Break down complex logic into small, testable functions.
*   **Local Variables:** Use `local` for variables inside functions to avoid polluting the global scope.

## 3. Portability
*   **Shebang:** Use `#!/usr/bin/env bash` for portability.
*   **Path Resolution:** Be aware of `readlink` vs `realpath` differences on macOS (BSD) vs Linux (GNU). Prefer portable solutions or explicit checks.

## 4. Style
*   **Indentation:** Use 4 spaces.
*   **Naming:**
    *   Variables: `UPPER_CASE` for globals/env, `lower_case` for locals.
    *   Functions: `snake_case`.
