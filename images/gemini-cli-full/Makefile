IMAGE_NAME := gemini-toolbox/cli-full
IMAGE_TAG := latest

.DEFAULT_GOAL := help

.PHONY: help build rebuild pre-build scan

help:
	@echo "Gemini CLI Full (Stack) Docker Toolbox"
	@echo "======================================"
	@echo "  make build    : Build the Docker image (cached)"
	@echo "  make rebuild  : Force rebuild without cache"
	@echo "  make scan     : Run security scan (Trivy) on this image"
	@echo "  make help     : Show this help message"

pre-build:
	cp ../gemini-cli/docker-entrypoint.sh .

build: pre-build
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

rebuild: pre-build
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

tag-version:
	@VERSION=$$(docker run --rm --entrypoint="" $(IMAGE_NAME):$(IMAGE_TAG) gemini --version | tr -d '\r'); \
	echo ">> Detected version: $$VERSION"; \
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):$$VERSION

ci: rebuild tag-version

scan:
	@echo ">> Scanning $(IMAGE_NAME):$(IMAGE_TAG)..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image --exit-code 1 --ignore-unfixed $(IMAGE_NAME):$(IMAGE_TAG)
