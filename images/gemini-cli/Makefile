IMAGE_NAME := gemini-cli
IMAGE_TAG := latest

# Set 'help' as the default target
.DEFAULT_GOAL := help

.PHONY: help build rebuild

help:
	@echo "Gemini CLI Docker Toolbox"
	@echo "========================="
	@echo "  make build    : Build the Docker image (cached)"
	@echo "  make rebuild  : Force rebuild without cache (updates CLI)"
	@echo "  make scan     : Run security scan (Trivy) on this image"
	@echo "  make help     : Show this help message"

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

rebuild:
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

scan:
	@echo ">> Scanning $(IMAGE_NAME):$(IMAGE_TAG)..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image --exit-code 1 --ignore-unfixed $(IMAGE_NAME):$(IMAGE_TAG)