# Master Makefile
# Orchestrates build tasks for all images in the repo

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Project Orchestration"
	@echo "====================="
	@echo "  make build       : Build ALL images (Base -> Stack -> Full & Light)"
	@echo "  make rebuild     : Force rebuild (no cache) of all images"
	@echo "  make scan        : Run security scan (Trivy) on built images"
	@echo "  make clean-cache : Prune the npm build cache (frees disk space)"

.PHONY: build
build:
	@echo ">> [1/4] Building gemini-base..."
	$(MAKE) -C images/gemini-base build
	@echo ">> [2/4] Building gemini-stack (depends on base)..."
	$(MAKE) -C images/gemini-stack build
	@echo ">> [3/4] Building gemini-cli (Light)..."
	$(MAKE) -C images/gemini-cli build
	@echo ">> [4/4] Building gemini-cli-full (depends on stack)..."
	$(MAKE) -C images/gemini-cli-full build

.PHONY: build
rebuild:
	@echo ">> [1/4] Rebuilding gemini-base..."
	$(MAKE) -C images/gemini-base rebuild
	@echo ">> [2/4] Rebuilding gemini-stack..."
	$(MAKE) -C images/gemini-stack rebuild
	@echo ">> [3/4] Rebuilding gemini-cli..."
	$(MAKE) -C images/gemini-cli rebuild
	@echo ">> [4/4] Rebuilding gemini-cli-full..."
	$(MAKE) -C images/gemini-cli-full rebuild

# Security Scan (Delegate to components)

.PHONY: scan
scan:

	@echo ">> Scanning gemini-base..."

	$(MAKE) -C images/gemini-base scan

	@echo ">> Scanning gemini-cli..."

	$(MAKE) -C images/gemini-cli scan

	@echo ">> Scanning gemini-cli-full..."

	$(MAKE) -C images/gemini-cli-full scan

.PHONY: clean-cache
clean-cache:
	@echo ">> Pruning gemini-npm-cache..."
	docker builder prune --force --filter id=gemini-npm-cache
