# ADR-0034: Automatic Inclusion of Worktree Root in Hub Discovery

## Status
Proposed

## Context
Gemini Hub allows users to browse project roots (defined in `HUB_ROOTS`) to launch new sessions. However, ephemeral worktrees created by the toolbox reside in a specific cache directory (`GEMINI_WORKTREE_ROOT`). Currently, if a user wants to connect to or browse these worktrees via the Hub, they must manually add the cache path to their scannable workspaces. This creates friction and is non-intuitive.

## Decision
We will modify the `Gemini Hub` configuration logic to automatically include the `WORKTREE_ROOT` in the `HUB_ROOTS` list during application initialization.

## Consequences
- **User Experience:** Ephemeral worktrees will be scannable by default without manual configuration.
- **Security:** Since the Hub already has access to the `WORKTREE_ROOT` for pruning and maintenance, adding it to the scannable list does not introduce new filesystem access risks beyond what is already granted.
- **Consistency:** Ensures that the Hub's "Discovery" capability matches the toolbox's "Worktree" capability.
