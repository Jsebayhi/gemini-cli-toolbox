variable "IMAGE_TAG" {
  default = "latest"
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
  # SLSA Provenance & SBOM: Automated build metadata and package inventory
  attest = [
    "type=provenance,mode=max",
    "type=sbom"
  ]
}

# Targets that need the bin/ directory context
target "_with_bin" {
  inherits = ["_common"]
  contexts = {
    bin = "bin"
  }
}

# --- Real Targets ---

target "base" {
  inherits = ["_common"]
  context  = "images/gemini-base"
  tags     = ["gemini-cli-toolbox/base:${IMAGE_TAG}"]
}

target "hub" {
  inherits = ["_with_bin"]
  context  = "images/gemini-hub"
  tags     = ["gemini-cli-toolbox/hub:${IMAGE_TAG}"]
}

target "cli" {
  inherits = ["_with_bin"]
  context  = "images/gemini-cli"
  contexts = {
    "gemini-cli-toolbox/base:${IMAGE_TAG}" = "target:base"
  }
  tags     = ["gemini-cli-toolbox/cli:${IMAGE_TAG}"]
}

target "cli-preview" {
  inherits = ["_with_bin"]
  context  = "images/gemini-cli-preview"
  contexts = {
    "gemini-cli-toolbox/base:${IMAGE_TAG}" = "target:base"
  }
  tags     = ["gemini-cli-toolbox/cli-preview:${IMAGE_TAG}"]
}

target "hub-test" {
  inherits   = ["_common"]
  context    = "images/gemini-hub"
  dockerfile = "tests/Dockerfile"
  tags       = ["gemini-hub-test:latest"]
}

target "bash-test" {
  inherits = ["_common"]
  context  = "tests/bash"
  tags     = ["gemini-bash-tester:latest"]
}
