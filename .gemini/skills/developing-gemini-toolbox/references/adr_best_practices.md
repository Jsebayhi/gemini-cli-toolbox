# ADR Best Practices

This guide establishes the mandatory standards for Architecture Decision Records (ADRs) in the Gemini CLI Toolbox. ADRs are not just documentation; they are an immutable audit trail of the system's evolution.

## 1. Immutability Mandate
**Rule:** Once an ADR is merged into the `main` branch, its **Context** and **Decision** sections are frozen forever.

- **Why?** Modifying a merged ADR erases history. It makes it impossible for future maintainers to understand *why* the system was in a certain state at a specific point in time.
- **How to change a decision?** You MUST create a NEW ADR that documents the new direction and explicitly supersedes the old one.

## 2. The Supersede Pattern
When a new decision overrides or significantly modifies a previous one, follow this exact protocol:

1.  **Old ADR:** Update the `Status` field to include `Superseded by [ADR-XXXX]`.
    - *Example:* `Status: Accepted (Superseded by [ADR-0052])`
2.  **New ADR:** Include a `Supersedes` field in the header pointing to the old record.
    - *Example:* `Supersedes: [ADR-0012]`
3.  **Preserve the Chain:** Never remove existing "Supersedes" lines from an old ADR. Maintain the full lineage (e.g., "Supersedes ADR-0001" and "Superseded by ADR-0038").

## 3. Alternative Analysis
**Rule:** Every ADR must analyze at least **3 distinct architectural alternatives**.

- **Naive/Simple:** The "quick fix" or standard approach.
- **Robust/Scalable:** The "enterprise" or long-term approach.
- **Novel/Hack:** A creative or project-specific alternative.

For every non-selected alternative, you MUST provide a clear **Reason for Rejection**.

## 4. Security & Privilege Analysis
If the decision impacts networking, file permissions, or system capabilities (e.g., `NET_ADMIN`, `DooD`), the ADR **must** include a dedicated Security Analysis section.

- **Risk Assessment:** What is the worst-case scenario if this component is compromised?
- **Mitigation:** How does the design minimize this risk?
- **Recommendation:** Clear guidance for users on the security trade-offs.

## 5. Naming & Formatting
- **Filename:** `NNNN-kebab-case-description.md` (e.g., `0052-tailscale-kernel-tun.md`).
- **Title:** Always start with `# ADR-NNNN: [Title]`.
- **Links:** Use relative links (`./0012-standalone-architecture.md`) for internal ADR references.
