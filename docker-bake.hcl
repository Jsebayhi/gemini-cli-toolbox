variable "IMAGE_TAG" {
  default = "latest"
}

variable "GEMINI_VERSION" {
  default = ""
}

# Default prefix for local builds
variable "REPO_PREFIX" {
  default = "gemini-cli-toolbox"
}

# Internal flag to switch between Local and Release naming.
variable "RELEASE_TYPE" {
  default = ""
}

# Set to true in CI to enable SBOM/Provenance
variable "ENABLE_ATTESTATIONS" {
  default = "false"
}

# --- Groups ---

group "default" {
  targets = ["base", "hub", "cli", "cli-preview", "hub-test", "bash-test"]
}

# --- Base Templates ---

target "_common" {
  args = {
    IMAGE_TAG = "${IMAGE_TAG}"
    BASE_TAG  = "${IMAGE_TAG}"
  }
  cache-from = ["type=gha"]
  cache-to   = ["type=gha,mode=max"]
}

target "_release" {
  inherits = ["_common"]
  attest = ENABLE_ATTESTATIONS == "true" ? ["type=provenance,mode=max", "type=sbom"] : []
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

# Internal intermediate image.
target "base" {
  inherits = ["_common"]
  context  = "images/gemini-base"
  tags     = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${IMAGE_TAG}-base" : "${REPO_PREFIX}/base:${IMAGE_TAG}"
  ]
}

target "hub" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-hub"
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${IMAGE_TAG}-hub" : "${REPO_PREFIX}/hub:${IMAGE_TAG}"
  ]
}

target "cli" {
  inherits = ["_release", "_with_bin", "_with_scripts"]
  context  = "images/gemini-cli"
  contexts = {
    "internal-base-build-scratchpad" = "target:base"
  }
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${IMAGE_TAG}-stable" : "${REPO_PREFIX}/cli:${IMAGE_TAG}",
    RELEASE_TYPE == "suffix" && GEMINI_VERSION != "" ? "${REPO_PREFIX}:${GEMINI_VERSION}-stable" : ""
  ]
}

target "cli-preview" {
  inherits = ["_release", "_with_bin", "_with_scripts"]
  context  = "images/gemini-cli-preview"
  contexts = {
    "internal-base-build-scratchpad" = "target:base"
  }
  tags = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${IMAGE_TAG}-preview" : "${REPO_PREFIX}/cli-preview:${IMAGE_TAG}",
    RELEASE_TYPE == "suffix" && GEMINI_VERSION != "" ? "${REPO_PREFIX}:${GEMINI_VERSION}-preview" : ""
  ]
}

# Test Runners (Also respect REPO_PREFIX for PR verification)
target "hub-test" {
  inherits   = ["_common"]
  context    = "images/gemini-hub"
  dockerfile = "tests/Dockerfile"
  tags       = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${IMAGE_TAG}-hub-test" : "${REPO_PREFIX}/hub-test:${IMAGE_TAG}"
  ]
}

target "bash-test" {
  inherits = ["_common"]
  context  = "tests/bash"
  tags     = [
    RELEASE_TYPE == "suffix" ? "${REPO_PREFIX}:${IMAGE_TAG}-bash-test" : "${REPO_PREFIX}/bash-test:${IMAGE_TAG}"
  ]
}
