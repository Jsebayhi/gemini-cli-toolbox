# Master Makefile
# Orchestrates build tasks for all images in the repo

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Project Orchestration"
	@echo "====================="
	@echo "  make build         : Build ALL images (Parallelizable with -j)"
	@echo "  make rebuild       : Force rebuild ALL images (Parallelizable with -j)"
	@echo "  make scan          : Run security scan (Trivy)"
	@echo "  make local-ci      : Run mandatory pre-PR checks (Lint & Test)"
	@echo "  make docker-readme : Generate README_DOCKER.md with absolute links"
	@echo "  make clean-cache   : Prune npm build cache"
	@echo ""
	@echo "Parallel Build Example:"
	@echo "  make -j4 build"

# --- Documentation ---

.PHONY: docker-readme
docker-readme:
	@echo ">> Generating README_DOCKER.md..."
	cp README.md README_DOCKER.md
	# Replace relative links with absolute GitHub links
	sed -i 's|(docs/|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/docs/|g' README_DOCKER.md
	sed -i 's|(adr/|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/adr/|g' README_DOCKER.md
	sed -i 's|(docs/CONTRIBUTING.md)|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/docs/CONTRIBUTING.md)|g' README_DOCKER.md

# --- Build Targets (Incremental) ---

.PHONY: build-base
build-base:
	@echo ">> Building gemini-base..."
	$(MAKE) -C images/gemini-base build

.PHONY: build-cli
build-cli: build-base
	@echo ">> Building gemini-cli (Light)..."
	$(MAKE) -C images/gemini-cli build

.PHONY: build-cli-preview
build-cli-preview: build-base
	@echo ">> Building gemini-cli-preview..."
	$(MAKE) -C images/gemini-cli-preview build

.PHONY: build-hub
build-hub:
	@echo ">> Building gemini-hub..."
	$(MAKE) -C images/gemini-hub build

# Main Build Entrypoint
.PHONY: build
build: build-cli build-cli-preview build-hub

# --- Rebuild Targets (No Cache) ---

.PHONY: rebuild-base
rebuild-base:
	@echo ">> Rebuilding gemini-base..."
	$(MAKE) -C images/gemini-base rebuild

.PHONY: rebuild-cli
rebuild-cli: rebuild-base
	@echo ">> Rebuilding gemini-cli..."
	$(MAKE) -C images/gemini-cli rebuild

.PHONY: rebuild-cli-preview
rebuild-cli-preview: rebuild-base
	@echo ">> Rebuilding gemini-cli-preview..."
	$(MAKE) -C images/gemini-cli-preview rebuild

.PHONY: rebuild-hub
rebuild-hub:
	@echo ">> Rebuilding gemini-hub..."
	$(MAKE) -C images/gemini-hub rebuild

# Main Rebuild Entrypoint
.PHONY: rebuild
rebuild: rebuild-cli rebuild-cli-preview rebuild-hub

# --- Fast Update Targets (App Layer Only) ---

.PHONY: rebuild-cli-only
rebuild-cli-only:
	@echo ">> Rebuilding gemini-cli (App Layer)..."
	$(MAKE) -C images/gemini-cli rebuild

.PHONY: rebuild-cli-preview-only
rebuild-cli-preview-only:
	@echo ">> Rebuilding gemini-cli-preview (App Layer)..."
	$(MAKE) -C images/gemini-cli-preview rebuild

# Rebuild only the applications (Parallelizable)
.PHONY: rebuild-gemini-cli
rebuild-gemini-cli: rebuild-cli-only rebuild-cli-preview-only

# --- Quality Assurance (Lint & Test) ---

.PHONY: lint
lint: lint-shell lint-python

.PHONY: lint-shell
lint-shell:
	@echo ">> Linting Bash Scripts (ShellCheck)..."
	docker run --rm -v "$(shell pwd):/mnt" -w /mnt koalaman/shellcheck bin/gemini-toolbox bin/gemini-hub images/gemini-cli/docker-entrypoint.sh images/gemini-hub/docker-entrypoint.sh

.PHONY: lint-python
lint-python:
	@echo ">> Linting Python Code (Ruff)..."
	docker run --rm -v "$(shell pwd):/mnt" -w /mnt ghcr.io/astral-sh/ruff check images/gemini-hub

.PHONY: test
test:
	$(MAKE) -C images/gemini-hub test

# --- Mandatory Pre-PR Check ---
.PHONY: local-ci
local-ci: lint test
	@echo ">> All mandatory checks passed. Ready for PR."

# --- CI Targets (Full Rebuild + Tag) ---

.PHONY: ci-cli
ci-cli: rebuild-base
	@echo ">> CI: Building & Tagging gemini-cli..."
	$(MAKE) -C images/gemini-cli ci

.PHONY: ci-preview
ci-preview: rebuild-base
	@echo ">> CI: Building & Tagging gemini-cli-preview..."
	$(MAKE) -C images/gemini-cli-preview ci

.PHONY: ci-hub
ci-hub:
	@echo ">> CI: Building gemini-hub..."
	$(MAKE) -C images/gemini-hub ci

# Main CI Entrypoint
.PHONY: ci
ci: ci-cli ci-preview ci-hub

.PHONY: print-image-cli
print-image-cli:
	@$(MAKE) -C images/gemini-cli -s print-image

.PHONY: print-image-preview
print-image-preview:
	@$(MAKE) -C images/gemini-cli-preview -s print-image

.PHONY: print-image-hub
print-image-hub:
	@$(MAKE) -C images/gemini-hub -s print-image

# Security Scan (Delegate to components)
.PHONY: scan
scan:
	@echo ">> Scanning gemini-base..."
	$(MAKE) -C images/gemini-base scan
	@echo ">> Scanning gemini-cli..."
	$(MAKE) -C images/gemini-cli scan
	@echo ">> Scanning gemini-cli-preview..."
	$(MAKE) -C images/gemini-cli-preview scan
	@echo ">> Scanning gemini-hub..."
	$(MAKE) -C images/gemini-hub scan

.PHONY: clean-cache
clean-cache:
	@echo ">> Pruning gemini-npm-cache..."
	docker builder prune --force --filter id=gemini-npm-cache