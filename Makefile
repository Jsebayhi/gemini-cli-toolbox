# Master Makefile
# Single Source of Truth for Build, Lint, and Test

# Default target
.DEFAULT_GOAL := help

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
test-bash: deps-bash
	@echo ">> Running Bash Automated Tests..."
	docker buildx bake bash-test
	mkdir -p coverage/bash
	docker run --rm \
		--cap-add=SYS_PTRACE \
		-v "$(shell pwd):/code" \
		-w /code \
		--entrypoint kcov \
		gemini-bash-tester:latest \
		--include-path=/code/bin,/code/images \
		/code/coverage/bash \
		bats tests/bash

.PHONY: test-hub
test-hub:
	@echo ">> Running Gemini Hub Tests..."
	docker buildx bake hub-test
	mkdir -p coverage/python
	docker run --rm \
		-v "$(shell pwd)/coverage/python:/coverage" \
		gemini-hub-test:latest \
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

.PHONY: build
build:
	@echo ">> Building all images via Docker Bake..."
	docker buildx bake

.PHONY: build-base
build-base:
	@echo ">> Building gemini-base..."
	docker buildx bake base

.PHONY: build-hub
build-hub:
	@echo ">> Building gemini-hub..."
	docker buildx bake hub

.PHONY: build-cli
build-cli:
	@echo ">> Building gemini-cli..."
	docker buildx bake cli

.PHONY: build-cli-preview
build-cli-preview:
	@echo ">> Building gemini-cli-preview..."
	docker buildx bake cli-preview

.PHONY: build-test-images
build-test-images:
	@echo ">> Building test runner images..."
	docker buildx bake bash-test hub-test

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

.PHONY: local-ci
local-ci: lint build test
	@echo ">> All local checks passed."
