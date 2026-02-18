variable "IMAGE_TAG" {
  default = "latest"
}

variable "GEMINI_VERSION" {
  default = ""
}

variable "DOCKER_HUB_REPO" {
  default = "jsebayhi/gemini-cli-toolbox"
}

# Set to true in CI to enable SBOM/Provenance
variable "ENABLE_ATTESTATIONS" {
  default = false
}

# --- Groups ---

group "default" {
  targets = ["base", "hub", "cli", "cli-preview", "hub-test", "bash-test"]
}

# --- Base Templates ---

# Operational Efficiency (Cache & Args) - Essential for everyone
target "_common" {
  args = {
    IMAGE_TAG = "${IMAGE_TAG}"
    BASE_TAG  = "${IMAGE_TAG}"
  }
  cache-from = ["type=gha"]
  cache-to   = ["type=gha,mode=max"]
}

# Production Integrity (SLSA: Provenance & SBOM) - Only for released images
target "_release" {
  inherits = ["_common"]
  attest = ENABLE_ATTESTATIONS ? ["type=provenance,mode=max", "type=sbom"] : []
}

# Artifact Layer (bin/ directory)
target "_with_bin" {
  contexts = {
    bin = "bin"
  }
}

# --- Real Targets ---

# Internal intermediate image (not released to public).
# Inherits only cache settings to avoid SLSA overhead on non-public artifacts.
target "base" {
  inherits = ["_common"]
  context  = "images/gemini-base"
  tags     = ["gemini-cli-toolbox/base:${IMAGE_TAG}"]
}

target "hub" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-hub"
  tags     = ["${DOCKER_HUB_REPO}:latest-hub"]
}

target "cli" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-cli"
  contexts = {
    "gemini-cli-toolbox/base:${IMAGE_TAG}" = "target:base"
  }
  tags = [
    "${DOCKER_HUB_REPO}:latest-stable",
    GEMINI_VERSION != "" ? "${DOCKER_HUB_REPO}:${GEMINI_VERSION}-stable" : ""
  ]
}

target "cli-preview" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-cli-preview"
  contexts = {
    "gemini-cli-toolbox/base:${IMAGE_TAG}" = "target:base"
  }
  tags = [
    "${DOCKER_HUB_REPO}:latest-preview",
    GEMINI_VERSION != "" ? "${DOCKER_HUB_REPO}:${GEMINI_VERSION}-preview" : ""
  ]
}

# Test Runners (Fast & Lean - No SLSA overhead)
target "hub-test" {
  inherits   = ["_common"]
  context    = "images/gemini-hub"
  dockerfile = "tests/Dockerfile"
  tags       = ["gemini-hub-test:${IMAGE_TAG}"]
}

target "bash-test" {
  inherits = ["_common"]
  context  = "tests/bash"
  tags     = ["gemini-bash-tester:${IMAGE_TAG}"]
}
