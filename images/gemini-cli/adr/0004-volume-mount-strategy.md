# ADR 0004: Configuration Volume Strategy

## Status
Accepted

## Date
2025-12-17

## Context
We need to persist the user's authentication and configuration between container runs. However, mounting the entire configuration folder can lead to performance issues if the application performs synchronous I/O on large history files.

## Decision
We mount the host's configuration directory (e.g., `~/.gemini`) to a specific subdirectory **`/home/gemini/.gemini`** inside the container, while creating the rest of `/home/gemini` as ephemeral container storage.

## Alternatives Considered
*   **Mounting `/home/gemini` (Entire Home):**
    *   *Cons:* Pollutes the host folder with container-specific dotfiles (`.config`, `.npm`, `.cache`).
    *   *Cons:* Can cause permission conflicts if the image's internal layout changes.
*   **Mounting Config + Cache:**
    *   *Cons:* Mounting large cache/history folders via Docker Bind Mounts caused severe input lag.

## Consequences
*   **Persistence:** Auth tokens are saved to the host.
*   **Performance:** High-frequency ephemeral I/O (in `~/.npm` or `~/.config`) usually happens on the fast container filesystem (unless the app writes specifically to `~/.gemini`).
*   **Constraint:** The user must ensure the mounted `~/.gemini` folder does not become excessively large (e.g., >500MB log files), as this will re-introduce I/O lag.
