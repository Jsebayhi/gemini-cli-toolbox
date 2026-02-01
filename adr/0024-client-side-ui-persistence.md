# 24. Client-Side UI Persistence

Date: 2026-02-01
Status: Accepted

## Context
The Gemini Hub is designed as a lightweight, stateless discovery tool. However, users—especially on mobile devices—experience friction when repeatedly navigating deep directory structures to launch common sessions. There is a need to remember "Recent Paths" or user preferences to improve UX.

We needed to decide where to store this state:
1.  **Server-Side (File/DB):** Store history in a volume mounted to the Hub container.
2.  **Client-Side (Browser):** Store history in `localStorage`/`cookies`.

## Decision
We chose to implement **Client-Side Persistence** using `localStorage`.

## Consequences

### Positive
*   **Zero Server State:** The Hub container remains ephemeral and stateless. It can be destroyed/recreated without losing user data (since data is on the user's device).
*   **Privacy/Isolation:** In a scenario where multiple users access the same Hub (e.g., on a LAN), User A does not see User B's recent paths.
*   **Simplicity:** No database migrations, file locking, or volume permission management required on the backend.

### Negative
*   **Device Fragmentation:** History is not synced between devices. A path launched on Desktop is not visible on Mobile.
*   **Browser Dependency:** Clearing browser data erases the history.

## Technical Details
*   **Key:** `recentPaths` (JSON array of strings).
*   **Limit:** Frontend logic enforces a limit (e.g., MRU 3 items) to prevent storage bloat.
*   **Sensitivity:** Only file paths are stored. No sensitive credentials should ever be stored in `localStorage`.
