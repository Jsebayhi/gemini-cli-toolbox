IMAGE_NAME := gemini-base
IMAGE_TAG := latest

.DEFAULT_GOAL := help

.PHONY: help build rebuild scan

help:
	@echo "Gemini Base Image"
	@echo "================="
	@echo "  make build    : Build the Base image (OS + Sys Tools)"
	@echo "  make rebuild  : Force rebuild without cache (OS Updates)"
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