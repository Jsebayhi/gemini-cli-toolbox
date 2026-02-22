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
    BASE_IMAGE = "base-image"
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
  tags     = ["gemini-cli-toolbox/base:${get_tag(GITHUB_REF)}"]
}

target "hub" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-hub"
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${get_tag(GITHUB_REF)}-hub" : "${REPO_PREFIX}/hub:${get_tag(GITHUB_REF)}"
  ]
}

target "cli" {
  inherits = ["_release", "_with_bin", "_with_scripts"]
  context  = "images/gemini-cli"
  contexts = {
    base-image = "target:base"
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
    base-image = "target:base"
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
  tags       = ["gemini-cli-toolbox/hub-test:${get_tag(GITHUB_REF)}"]
}

target "bash-test" {
  inherits = ["_common"]
  context  = "tests/bash"
  tags     = ["gemini-cli-toolbox/bash-test:${get_tag(GITHUB_REF)}"]
}
