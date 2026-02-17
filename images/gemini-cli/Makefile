IMAGE_NAME := gemini-cli-toolbox/cli

# Detect Branch and Suffix Tag
CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
SAFE_BRANCH := $(shell echo $(CURRENT_BRANCH) | sed 's/[^a-zA-Z0-9]/-/g')

ifeq ($(CURRENT_BRANCH),main)
    IMAGE_TAG := latest
else
    IMAGE_TAG := latest-$(SAFE_BRANCH)
endif

# Set 'help' as the default target
.DEFAULT_GOAL := help

.PHONY: help build rebuild

help:
	@echo "Gemini CLI Toolbox"
	@echo "========================="
	@echo "  make build    : Build the Docker image (cached)"
	@echo "  make rebuild  : Force rebuild without cache (updates CLI)"
	@echo "  make scan     : Run security scan (Trivy) on this image"
	@echo "  make help     : Show this help message"

build:
	docker build --build-arg BASE_TAG=$(IMAGE_TAG) -t $(IMAGE_NAME):$(IMAGE_TAG) .

rebuild:
	docker build --build-arg BASE_TAG=$(IMAGE_TAG) --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

tag-version:
	@VERSION=$$(docker run --rm --entrypoint="" $(IMAGE_NAME):$(IMAGE_TAG) gemini --version | tr -d '\r'); \
	echo ">> Detected version: $$VERSION"; \
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):$$VERSION

print-tag:
	@echo $(IMAGE_TAG)

print-image:
	@echo $(IMAGE_NAME):$(IMAGE_TAG)

ci: rebuild
	$(MAKE) tag-version

scan:
	@echo ">> Scanning $(IMAGE_NAME):$(IMAGE_TAG)..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v "$(shell pwd)/../../.trivyignore:/.trivyignore" \
		aquasec/trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed --ignorefile /.trivyignore $(IMAGE_NAME):$(IMAGE_TAG)
