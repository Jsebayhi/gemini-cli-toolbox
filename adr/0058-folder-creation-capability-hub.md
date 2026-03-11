# ADR-0058: Folder Creation Capability in Gemini Hub

## Status
Proposed

## Context
The Gemini Hub allows users to browse their workspace roots and select a project directory to launch a session. However, users currently cannot create new project directories directly from the Hub UI. This requires them to switch to a terminal or file manager to create a folder before they can use it in the Hub, creating friction in the developer workflow.

## Decision
We will implement the capability to create new directories directly from the Gemini Hub's wizard step during the browsing phase.

### Implementation Details

1.  **Backend Service:** Add `create_directory(parent_path, name)` to `FileSystemService`.
    *   **Validation:** The `parent_path` must be within the configured `HUB_ROOTS`.
    *   **Sanitization:** The `name` must not contain path separators (`/`) or relative path segments (`..`).
    *   **Atomicity:** Use `os.mkdir` to ensure only one level of directory is created and to prevent accidental recursive creation.

2.  **API Route:** Add a POST endpoint `/api/create-directory`.
    *   Request body: `{ "parent_path": "...", "name": "..." }`
    *   Response: Success or error message.

3.  **UI Integration:**
    *   Add a "New Folder" button to the Step 2 (Browse) footer of the Launch Wizard.
    *   Use a simple browser `prompt()` for the folder name to keep the implementation lightweight and consistent with the existing minimal UI.
    *   Refresh the folder list automatically upon successful creation.

## Consequences

### Positive
*   **Reduced Friction:** Users can start new projects from scratch without leaving the Hub UI.
*   **Workflow Integration:** Better aligns with the "Toolbox" philosophy of providing all necessary utilities in one place.

### Negative/Risks
*   **Write Access:** The Hub container must have write permissions to the workspace roots.
*   **Security:** Incorrect validation could allow directory creation outside of allowed roots.

## Alternatives Considered

1.  **Full File Manager:** Implementing a full-featured file manager (rename, delete, move) was considered but rejected as it increases complexity and security surface area beyond the immediate need for project initialization.
2.  **Recursive Creation:** Allowing `os.makedirs` was considered but `os.mkdir` is safer as it prevents creating deep hierarchies in one go, which is less likely to be intentional for a single "New Folder" action.
3.  **Custom UI Dialog:** A custom modal for the folder name was considered but `prompt()` is sufficient for this MVP and avoids adding more boilerplate to the frontend.
