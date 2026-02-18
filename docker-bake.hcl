variable "IMAGE_TAG" {
  default = "latest"
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
  attest = [
    "type=provenance,mode=max",
    "type=sbom"
  ]
}

# Artifact Layer (bin/ directory)
target "_with_bin" {
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
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-hub"
  tags     = ["gemini-cli-toolbox/hub:${IMAGE_TAG}"]
}

target "cli" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-cli"
  contexts = {
    "gemini-cli-toolbox/base:${IMAGE_TAG}" = "target:base"
  }
  tags     = ["gemini-cli-toolbox/cli:${IMAGE_TAG}"]
}

target "cli-preview" {
  inherits = ["_release", "_with_bin"]
  context  = "images/gemini-cli-preview"
  contexts = {
    "gemini-cli-toolbox/base:${IMAGE_TAG}" = "target:base"
  }
  tags     = ["gemini-cli-toolbox/cli-preview:${IMAGE_TAG}"]
}

# Test Runners (Fast & Lean - No SLSA overhead)
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
