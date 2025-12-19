# Master Makefile
# Orchestrates build tasks for all images in the repo

# Targets
.PHONY: help build rebuild

.DEFAULT_GOAL := help

help:
	@echo "Project Orchestration"
	@echo "====================="
	@echo "  make build    : Build the gemini-cli image"
	@echo "  make rebuild  : Force rebuild (no cache) the gemini-cli image"
	@echo "  make help     : Show this help message"

build:
	@echo ">> Building gemini-cli..."
	$(MAKE) -C images/gemini-cli build

rebuild:
	@echo ">> Rebuilding gemini-cli (no cache)..."
	$(MAKE) -C images/gemini-cli rebuild
