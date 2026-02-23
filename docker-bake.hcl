# --- Variables ---

variable "IMAGE_TAG" {
  default = "latest"
}

# The raw Git reference (e.g., refs/heads/main or refs/pull/1/merge)
variable "GITHUB_REF" {
  default = ""
}

# The GitHub event name (e.g., push, pull_request, schedule)
variable "GITHUB_EVENT_NAME" {
  default = ""
}

variable "GEMINI_VERSION" {
  default = ""
}

# Default prefix for local builds (matches main's sub-directory convention)
variable "REPO_PREFIX" {
  default = "gemini-cli-toolbox"
}

# Internal flag to switch between Local (sub-repo) and Release (flat with suffix) naming.
variable "RELEASE_TYPE" {
  default = ""
}

# Set to true in CI to enable SBOM/Provenance
variable "ENABLE_ATTESTATIONS" {
  default = "false"
}

# --- Functions ---

# Computes the safe tag name from a git ref.
# Logic: 
# 1. If it's the main branch, return 'latest'.
# 2. Otherwise, return 'latest-<sanitized-ref>'.
function "get_tag" {
  params = [ref]
  result = (ref == "refs/heads/main" || ref == "") ? "latest" : "latest-${regex_replace(regex_replace(ref, "^refs/(heads|pull)/", ""), "[^a-zA-Z0-9]", "-")}"
}

# --- Groups ---

group "default" {
  targets = ["base", "hub", "cli", "cli-preview", "hub-test", "bash-test"]
}

# --- Base Templates ---

target "_common" {
  args = {
    IMAGE_TAG = get_tag(GITHUB_REF)
    BASE_TAG  = get_tag(GITHUB_REF)
    # The ARG Pattern (ADR-0045): Use a public fallback for base images.
    BASE_IMAGE = "local-base-${get_tag(GITHUB_REF)}:latest"
  }
  cache-from = ["type=gha"]
  cache-to   = ["type=gha,mode=max"]
}

target "_release" {
  inherits = ["_common"]
  attest = ENABLE_ATTESTATIONS ? ["type=provenance,mode=max", "type=sbom"] : []
}

target "_with_bin" {
  contexts = {
    bin = "bin"
  }
}

target "_with_scripts" {
  contexts = {
    scripts = "images/gemini-cli"
  }
}

# --- Real Targets ---

# Internal intermediate image (not released to public).
target "base" {
  inherits = ["_common"]
  context  = "images/gemini-base"
  args = {
    BASE_IMAGE = "python:slim"
  }
  # Context Isolation: Branch-prefixed tag to prevent build pollution on shared runners.
  tags     = ["local-base-${get_tag(GITHUB_REF)}:latest"]
}

target "hub" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-hub"
  args = {
    BASE_IMAGE = "python:3.11-slim-bookworm"
  }
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${get_tag(GITHUB_REF)}-hub" : "${REPO_PREFIX}/hub:${get_tag(GITHUB_REF)}"
  ]
}

target "cli" {
  inherits = ["_release", "_with_bin", "_with_scripts"]
  context  = "images/gemini-cli"
  # Map the BASE_IMAGE argument to the branch-prefixed local target.
  contexts = {
    "local-base-${get_tag(GITHUB_REF)}:latest" = "target:base"
  }
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${get_tag(GITHUB_REF)}-stable" : "${REPO_PREFIX}/cli:${get_tag(GITHUB_REF)}",
    RELEASE_TYPE == "suffix" && GEMINI_VERSION != "" ? "${REPO_PREFIX}:${GEMINI_VERSION}-stable" : ""
  ]
}

target "cli-preview" {
  inherits = ["_release", "_with_bin", "_with_scripts"]
  context  = "images/gemini-cli-preview"
  contexts = {
    "local-base-${get_tag(GITHUB_REF)}:latest" = "target:base"
  }
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${get_tag(GITHUB_REF)}-preview" : "${REPO_PREFIX}/cli-preview:${get_tag(GITHUB_REF)}",
    RELEASE_TYPE == "suffix" && GEMINI_VERSION != "" ? "${REPO_PREFIX}:${GEMINI_VERSION}-preview" : ""
  ]
}

# Test Runners
target "hub-test" {
  inherits   = ["_common"]
  context    = "images/gemini-hub"
  dockerfile = "tests/Dockerfile"
  tags       = ["local-hub-test-${get_tag(GITHUB_REF)}:latest"]
}

target "bash-test" {
  inherits = ["_common"]
  context  = "tests/bash"
  tags     = ["local-bash-test-${get_tag(GITHUB_REF)}:latest"]
}
