# ADR 0010: Configuration Profiles and Extra Args

## Status
Accepted

## Context
Users need a way to maintain separate environments for different contexts (e.g., "Personal" vs "Work").
We previously established the use of `--config` to specify a configuration directory (`HOST_CONF_DIR`), which isolates:
*   CLI History
*   Prompts
*   Authentication Tokens

However, users also need to customize the **runtime environment** per profile. Common requirements include:
*   Mounting specific host directories (e.g., a "Work" documents folder).
*   Setting specific environment variables.
*   Enforcing specific toolbox flags (e.g., always use `--preview` image).

Before this ADR, users had to pass these arguments manually every time they invoked the toolbox, or create wrapper scripts. The `gemini-hub` also had no way to know which additional volumes were required for a specific profile.

## Decision
We introduce a standard mechanism for defining persistent, profile-specific arguments via a file named `extra-args` located within the configuration directory.

### 1. File Location & Structure
The directory structure depends on the flag used to specify the configuration. **These flags are mutually exclusive.**

**A. Profile Mode (`--profile <PATH>`)**
Used for full environment management.
```text
~/.gemini-profiles/work/       <-- Passed to --profile
├── extra-args                 # Arguments for the toolbox
├── .gemini/                   # The actual config dir (Auto-managed: history, cookies)
└── secrets/                   # User files (can be mounted via extra-args)
```
*   **Behavior:**
    *   `gemini-toolbox` reads `.../work/extra-args`.
    *   `gemini-toolbox` mounts `.../work/.gemini` to `/home/gemini/.gemini` inside the container.

**B. Config Mode (`--config <PATH>` or Default)**
Used for simple configuration directory overrides.
```text
~/.gemini-legacy/              <-- Passed to --config
├── history
├── .config/
└── ...
```
*   **Behavior:**
    *   `gemini-toolbox` mounts the directory **directly** to `/home/gemini/.gemini`.
    *   **No `extra-args` support.**
    *   **No `.gemini` nesting.**

### 2. Mutually Exclusive Flags
The script will exit with an error if both `--config` and `--profile` are provided in the same command line to avoid ambiguity.

### 3. Semantics: Toolbox Arguments
The contents of `extra-args` are treated as **arguments to the `gemini-toolbox` script**, not just raw Docker arguments.
*   **Why:** This provides maximum flexibility. Users can define volumes (`-v`), env vars (`-e`), or toolbox behaviors (`--no-ide`, `--preview`).
*   **Parsing:** One argument per line is recommended for readability, but space-separated arguments are supported. Comments (`#`) are ignored.

### 3. Precedence: CLI Overrides Profile
The arguments from `extra-args` are prepended to the command-line arguments.
*   **Order:** `[extra-args] [cli-args]`
*   **Effect:** Since the toolbox parses arguments sequentially, and later flags typically override earlier ones (e.g., `VARIANT="preview"`), explicit CLI arguments will override profile defaults.
*   **Exception:** Accumulative arguments (like `--volume` or `--docker-args`) are additive. Both the profile's volumes and the CLI's volumes will be mounted.

### 4. Implementation Details
The `gemini-toolbox` script performs a "Pre-scan" pass:
1.  Scans CLI arguments for `--config` to determine the target `HOST_CONF_DIR`.
2.  Reads `${HOST_CONF_DIR}/extra-args` into an array.
3.  Prepends this array to the original argument list (`set -- "${FILE_ARGS[@]}" "$@"`).
4.  Proceeds with standard argument parsing.

## Consequences
*   **Positive:** Profiles become self-contained "environments". A single directory holds both the state (history) and the definition (mounts/flags).
*   **Positive:** The Hub (and other tools) can blindly respect these settings without special logic.
*   **Negative:** Parsing complexity in `gemini-toolbox` increases slightly due to the pre-scan requirement.
*   **Negative:** Potential for infinite loops if `extra-args` contains `--config` pointing to itself (though the script logic naturally handles this by just setting the var again).

## Example
**File:** `~/.gemini-work/extra-args`
```text
--preview
--volume /home/user/work:/work
--env COMPANY_ID=123
```

**Command:**
```bash
gemini-toolbox --config ~/.gemini-work
```
**Effective Command:**
```bash
gemini-toolbox --preview --volume /home/user/work:/work --env COMPANY_ID=123 --config ~/.gemini-work
```