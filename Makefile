# Master Makefile
# Single Source of Truth for Build, Lint, and Test

# Default target
.DEFAULT_GOAL := help

# Detect Branch and Suffix Tag for image isolation
CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
SAFE_BRANCH := $(shell echo $(CURRENT_BRANCH) | sed 's/[^a-zA-Z0-9]/-/g')

# Human-First Defaults: Disable heavy SLSA attestations for local development.
# The CI overrides this via environment variables or command-line args.
export ENABLE_ATTESTATIONS ?= false

ifeq ($(CURRENT_BRANCH),main)
    export IMAGE_TAG := latest
else
    export IMAGE_TAG := latest-$(SAFE_BRANCH)
endif

# Detect if we need the advanced builder (only for SLSA/Attestations)
# Local development defaults to the native 'default' driver for instant incremental builds.
ifeq ($(ENABLE_ATTESTATIONS),true)
    BAKE_BUILDER := gemini-builder
    BAKE_FLAGS := --builder $(BAKE_BUILDER) --load
else
    BAKE_BUILDER := default
    BAKE_FLAGS := --builder default --load
endif

.PHONY: help
help:
	@echo "Project Orchestration"
	@echo "====================="
	@echo "  make build         : Build ALL images (Parallel via Docker Bake)"
	@echo "  make check-build   : Fast validation (Build to cache, NO image export)"
	@echo "  make rebuild       : Force rebuild ALL images from scratch"
	@echo "  make lint          : Run all linters (ShellCheck, Ruff)"
	@echo "  make test          : Run all tests (Bash, Hub)"
	@echo "  make local-ci      : Run everything (Lint + Build + Test)"
	@echo "  make scan          : Run security scan (Trivy)"
	@echo "  make docker-readme : Generate README_DOCKER.md"
	@echo "  make clean-cache   : Prune npm build cache"

# --- Quality Assurance ---

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
test: test-bash test-hub

.PHONY: test-bash
test-bash: setup-builder deps-bash
	@echo ">> Running Bash Automated Tests (Tag: ${IMAGE_TAG}, Builder: $(BAKE_BUILDER))..."
	docker buildx bake $(BAKE_FLAGS) bash-test
	mkdir -p coverage/bash
	docker run --rm \
		--cap-add=SYS_PTRACE \
		-v "$(shell pwd):/code" \
		-w /code \
		--entrypoint kcov \
		gemini-cli-toolbox/bash-test:${IMAGE_TAG} \
		--include-path=/code/bin,/code/images \
		/code/coverage/bash \
		bats tests/bash
	@echo ""
	@echo ">> Checking Bash Coverage (Threshold: 85%)..."
	@REPORT_JSON=$$(find coverage/bash -name "coverage.json" | head -n 1); \
	if [ -n "$$REPORT_JSON" ] && [ -f "$$REPORT_JSON" ]; then \
		COVERAGE=$$(cat "$$REPORT_JSON" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['percent_covered'])"); \
		echo "Percent covered: $$COVERAGE%"; \
		if python3 -c "import sys; exit(0 if float(sys.argv[1]) >= 85.0 else 1)" "$$COVERAGE"; then \
			echo ">> Coverage threshold (85%) PASSED."; \
		else \
			echo ">> Error: Coverage threshold (85%) FAILED (current: $$COVERAGE%)." >&2; \
			exit 1; \
		fi \
	else \
		echo ">> Warning: Coverage report not found."; \
	fi

.PHONY: test-hub
test-hub: setup-builder
	@echo ">> Running Gemini Hub Tests (Unit & Integration, Tag: ${IMAGE_TAG}, Builder: $(BAKE_BUILDER))..."
	docker buildx bake $(BAKE_FLAGS) hub-test
	mkdir -p coverage/python
	docker run --rm \
		-v "$(shell pwd)/coverage/python:/coverage" \
		gemini-cli-toolbox/hub-test:${IMAGE_TAG} \
		python3 -m pytest -n auto -vv \
		--cov=app \
		--cov-report=json:/coverage/coverage.json \
		--cov-fail-under=90 \
		tests/unit tests/integration

.PHONY: test-hub-ui
test-hub-ui:
	@echo ">> Running Gemini Hub UI Tests (Playwright)..."
	docker buildx bake $(BAKE_FLAGS) hub-test
	docker run --rm gemini-cli-toolbox/hub-test:${IMAGE_TAG} python3 -m pytest -n auto --reruns 1 -vv tests/ui

.PHONY: deps-bash
deps-bash:
	@if [ ! -d "tests/bash/libs/bats-support" ]; then \
		echo ">> Downloading bats-support v0.3.0..."; \
		mkdir -p tests/bash/libs; \
		curl -sL https://github.com/bats-core/bats-support/archive/refs/tags/v0.3.0.tar.gz | tar -xz -C tests/bash/libs; \
		mv tests/bash/libs/bats-support-0.3.0 tests/bash/libs/bats-support; \
	fi
	@if [ ! -d "tests/bash/libs/bats-assert" ]; then \
		echo ">> Downloading bats-assert v2.1.0..."; \
		mkdir -p tests/bash/libs; \
		curl -sL https://github.com/bats-core/bats-assert/archive/refs/tags/v2.1.0.tar.gz | tar -xz -C tests/bash/libs; \
		mv tests/bash/libs/bats-assert-2.1.0 tests/bash/libs/bats-assert; \
	fi

# --- Build Targets ---

# Ensure we use a builder that supports attestations (docker-container driver)
.PHONY: setup-builder
setup-builder:
	@if [ "$(BAKE_BUILDER)" = "gemini-builder" ]; then \
		if ! docker buildx inspect gemini-builder > /dev/null 2>&1; then \
			echo ">> Creating 'gemini-builder' (docker-container driver) for SLSA support..."; \
			docker buildx create --name gemini-builder --driver docker-container; \
		fi \
	fi

.PHONY: build
build: setup-builder
	@echo ">> Building all images via Docker Bake (Builder: $(BAKE_BUILDER))..."
	docker buildx bake $(BAKE_FLAGS)

.PHONY: check-build
check-build:
	@echo ">> Rapid Validation (Build to cache, Builder: default)..."
	docker buildx bake --builder default

.PHONY: rebuild
rebuild: setup-builder
	@echo ">> Rebuilding all images from scratch (no cache, Builder: $(BAKE_BUILDER))..."
	docker buildx bake $(BAKE_FLAGS) --no-cache

.PHONY: build-base
build-base: setup-builder
	@echo ">> Building gemini-base..."
	docker buildx bake $(BAKE_FLAGS) base

.PHONY: build-hub
build-hub: setup-builder
	@echo ">> Building gemini-hub..."
	docker buildx bake $(BAKE_FLAGS) hub

.PHONY: build-cli
build-cli: setup-builder
	@echo ">> Building gemini-cli..."
	docker buildx bake $(BAKE_FLAGS) cli

.PHONY: build-cli-preview
build-cli-preview: setup-builder
	@echo ">> Building gemini-cli-preview..."
	docker buildx bake $(BAKE_FLAGS) cli-preview

.PHONY: build-test-images
build-test-images: setup-builder
	@echo ">> Building test runner images..."
	docker buildx bake $(BAKE_FLAGS) bash-test hub-test

# --- Security & Docs ---

.PHONY: scan
scan:
	@echo ">> Scanning images (base, hub, cli)..."
	@for img in "gemini-cli-toolbox/base:latest" "gemini-cli-toolbox/hub:latest" "gemini-cli-toolbox/cli:latest"; do \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
			-v "$(shell pwd)/.trivyignore:/.trivyignore" \
			aquasec/trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed --ignorefile /.trivyignore $$img; \
	done

.PHONY: docker-readme
docker-readme:
	@echo ">> Generating README_DOCKER.md..."
	cp README.md README_DOCKER.md
	sed -i 's|(docs/|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/docs/|g' README_DOCKER.md
	sed -i 's|(adr/|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/adr/|g' README_DOCKER.md

.PHONY: clean-cache
clean-cache:
	@echo ">> Pruning gemini-npm-cache..."
	docker builder prune --force --filter id=gemini-npm-cache

.PHONY: local-ci
local-ci: lint build test
	@echo ">> All local checks passed."
