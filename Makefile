# Master Makefile
# Single Source of Truth for Build, Lint, and Test

# Default target
.DEFAULT_GOAL := help

# Detect Branch and Suffix Tag for image isolation
CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
SAFE_BRANCH := $(shell echo $(CURRENT_BRANCH) | sed 's/[^a-zA-Z0-9]/-/g')

# --- Configuration ---

# Human-First Defaults: Disable heavy SLSA attestations for local development.
export ENABLE_ATTESTATIONS ?= false

# Image tagging logic
ifeq ($(CURRENT_BRANCH),main)
    export IMAGE_TAG ?= latest
else
    export IMAGE_TAG ?= latest-$(SAFE_BRANCH)
endif

# Default prefix for local builds
export REPO_PREFIX ?= gemini-cli-toolbox

# Internal flag to switch between Local and Release naming.
export RELEASE_TYPE ?= 

# Builder logic: Use 'gemini-builder' (docker-container) for SLSA, else 'default'
export BUILDER_NAME ?= $(if $(filter true,$(ENABLE_ATTESTATIONS)),gemini-builder,default)

# Bake flags: '--load' exports to local daemon for tests.
# In CI, we override this to '--push' for main releases.
export BAKE_ACTION ?= --load
BAKE_FLAGS := --builder $(BUILDER_NAME) $(BAKE_ACTION)

# Image Names (Synced with docker-bake.hcl)
BASE_IMAGE       := $(if $(filter suffix,$(RELEASE_TYPE)),$(REPO_PREFIX):$(IMAGE_TAG)-base,$(REPO_PREFIX)/base:$(IMAGE_TAG))
HUB_IMAGE        := $(if $(filter suffix,$(RELEASE_TYPE)),$(REPO_PREFIX):$(IMAGE_TAG)-hub,$(REPO_PREFIX)/hub:$(IMAGE_TAG))
CLI_IMAGE        := $(if $(filter suffix,$(RELEASE_TYPE)),$(REPO_PREFIX):$(IMAGE_TAG)-stable,$(REPO_PREFIX)/cli:$(IMAGE_TAG))
PREVIEW_IMAGE    := $(if $(filter suffix,$(RELEASE_TYPE)),$(REPO_PREFIX):$(IMAGE_TAG)-preview,$(REPO_PREFIX)/cli-preview:$(IMAGE_TAG))
HUB_TEST_IMAGE   := $(if $(filter suffix,$(RELEASE_TYPE)),$(REPO_PREFIX):$(IMAGE_TAG)-hub-test,$(REPO_PREFIX)/hub-test:$(IMAGE_TAG))
BASH_TEST_IMAGE  := $(if $(filter suffix,$(RELEASE_TYPE)),$(REPO_PREFIX):$(IMAGE_TAG)-bash-test,$(REPO_PREFIX)/bash-test:$(IMAGE_TAG))

.PHONY: help
help:
	@echo "Project Orchestration"
	@echo "====================="
	@echo "  make build         : Build ALL images (Parallel via Docker Bake)"
	@echo "  make lint          : Run all linters (ShellCheck, Ruff)"
	@echo "  make test          : Run all tests (Bash, Hub)"
	@echo "  make local-ci      : Run everything (Lint + Build + Test)"
	@echo "  make scan          : Run security scan (Trivy)"
	@echo "  make docker-readme : Generate README_DOCKER.md"

# --- Quality Assurance ---

.PHONY: lint
lint:
	@echo ">> Linting Bash Scripts (ShellCheck)..."
	@docker run --rm -v "$(shell pwd):/mnt" -w /mnt koalaman/shellcheck bin/gemini-toolbox bin/gemini-hub
	@find images -name "*.sh" -print0 | xargs -0 -I {} docker run --rm -v "$(shell pwd):/mnt" -w /mnt koalaman/shellcheck "{}"
	@echo ">> Linting Python Code (Ruff)..."
	@docker run --rm -v "$(shell pwd):/mnt" -w /mnt ghcr.io/astral-sh/ruff check images/gemini-hub

.PHONY: test
test: test-bash test-hub

.PHONY: test-bash
test-bash: setup-builder deps-bash
	@echo ">> Running Bash Automated Tests (Tag: ${IMAGE_TAG}, Builder: $(BUILDER_NAME))..."
	@docker buildx bake $(BAKE_FLAGS) bash-test
	@mkdir -p coverage/bash
	@docker run --rm \
		--cap-add=SYS_PTRACE \
		-v "$(shell pwd)/bin:/code/bin" \
		-v "$(shell pwd)/images:/code/images" \
		-v "$(shell pwd)/tests/bash/test_entrypoint_cli.bats:/code/tests/bash/test_entrypoint_cli.bats" \
		-v "$(shell pwd)/tests/bash/test_entrypoint_hub.bats:/code/tests/bash/test_entrypoint_hub.bats" \
		-v "$(shell pwd)/tests/bash/test_helper.bash:/code/tests/bash/test_helper.bash" \
		-v "$(shell pwd)/tests/bash/test_hub_journeys.bats:/code/tests/bash/test_hub_journeys.bats" \
		-v "$(shell pwd)/tests/bash/test_hub_unit.bats:/code/tests/bash/test_hub_unit.bats" \
		-v "$(shell pwd)/tests/bash/test_hub.bats:/code/tests/bash/test_hub.bats" \
		-v "$(shell pwd)/tests/bash/test_toolbox_fidelity.bats:/code/tests/bash/test_toolbox_fidelity.bats" \
		-v "$(shell pwd)/tests/bash/test_toolbox_journeys.bats:/code/tests/bash/test_toolbox_journeys.bats" \
		-v "$(shell pwd)/tests/bash/test_toolbox_unit.bats:/code/tests/bash/test_toolbox_unit.bats" \
		-v "$(shell pwd)/tests/bash/test_toolbox.bats:/code/tests/bash/test_toolbox.bats" \
		-v "$(shell pwd)/coverage/bash:/code/coverage/bash" \
		-w /code \
		--entrypoint kcov \
		$(BASH_TEST_IMAGE) \
		--include-path=/code/bin,/code/images \
		/code/coverage/bash \
		bats tests/bash

.PHONY: test-hub
test-hub: setup-builder
	@echo ">> Running Gemini Hub Tests (Unit & Integration, Tag: ${IMAGE_TAG}, Builder: $(BUILDER_NAME))..."
	@docker buildx bake $(BAKE_FLAGS) hub-test
	@mkdir -p coverage/python
	@docker run --rm \
		-v "$(shell pwd)/coverage/python:/coverage" \
		$(HUB_TEST_IMAGE) \
		python3 -m pytest -n auto -vv \
		--cov=app \
		--cov-report=json:/coverage/coverage.json \
		--cov-fail-under=90 \
		tests/unit tests/integration

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

.PHONY: setup-builder
setup-builder:
	@if [ "$(BUILDER_NAME)" = "gemini-builder" ]; then \
		if ! docker buildx inspect gemini-builder > /dev/null 2>&1; then \
			echo ">> Creating 'gemini-builder' (docker-container driver) for SLSA support..."; \
			docker buildx create --name gemini-builder --driver docker-container --use; \
		fi \
	fi

.PHONY: build
build: setup-builder
	@echo ">> Building all images (Tag: ${IMAGE_TAG}, Builder: $(BUILDER_NAME))..."
	@docker buildx bake $(BAKE_FLAGS)

.PHONY: scan
scan:
	@echo ">> Scanning images (base, hub, cli, preview)..."
	@for img in "$(BASE_IMAGE)" "$(HUB_IMAGE)" "$(CLI_IMAGE)" "$(PREVIEW_IMAGE)"; do \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
			-v "$(shell pwd)/.trivyignore:/.trivyignore" \
			aquasec/trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed --ignorefile /.trivyignore $$img; \
	done

.PHONY: docker-readme
docker-readme:
	@echo ">> Generating README_DOCKER.md..."
	@cp README.md README_DOCKER.md
	@sed -i 's|(docs/|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/docs/|g' README_DOCKER.md
	@sed -i 's|(adr/|(https://github.com/Jsebayhi/gemini-cli-toolbox/blob/main/adr/|g' README_DOCKER.md

.PHONY: local-ci
local-ci: lint build test
	@echo ">> All local checks passed."
