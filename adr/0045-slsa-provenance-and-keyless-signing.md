# ADR-0045: SLSA Provenance and Keyless Signing

## Status
Accepted

## Context
Project images (CLI, Hub) were being pushed to Docker Hub without cryptographic proof of origin or build integrity. This left users vulnerable to potential supply-chain attacks if GitHub credentials were compromised.

## Decision
Implement a "Cost-Nothing" SLSA Level 3 equivalent security posture:
1.  **Provenance:** Enable BuildKit's `type=provenance` attestation in `docker-bake.hcl` to generate Level 1+ metadata (build logs, source repository, and commit hash).
2.  **SBOM:** Enable `type=sbom` attestation to automatically generate a Software Bill of Materials for every image, allowing users to audit for vulnerabilities.
3.  **Keyless Signing:** Use Cosign with GitHub's OIDC (OpenID Connect) token. This eliminates the need for manual key management or secrets for signing. 
4.  **Identity-Based Verification:** Sigstore/Cosign will issue short-lived certificates to the GitHub Action runner identity.

## Consequences
1.  **Trust:** Users can verify that images truly originated from the project's `main` branch.
2.  **Integrity:** The transparency log (Rekor) provides an immutable record of the build.
3.  **Governance:** Compliance with modern DevSecOps standards (SLSA) with zero operational overhead.

## Developer Experience (DX) Refinement
To maintain high developer velocity, SLSA attestations (SBOM/Provenance) are **disabled by default** for local builds. 
- **Reason:** Local Docker stores do not yet support loading attestations via the `--load` flag, which would force a slow export process or fail entirely.
- **Implementation:** The `Makefile` defaults `ENABLE_ATTESTATIONS` to `false`, allowing instant local cache hits using the native Docker driver. Attestations are explicitly enabled only in the CI environment for official releases.
