IMAGE_NAME := gemini-cli-toolbox/hub

# Detect Branch and Suffix Tag
CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
SAFE_BRANCH := $(shell echo $(CURRENT_BRANCH) | sed 's/[^a-zA-Z0-9]/-/g')

ifeq ($(CURRENT_BRANCH),main)
    IMAGE_TAG := latest
else
    IMAGE_TAG := latest-$(SAFE_BRANCH)
endif

DOCKER_FILE := Dockerfile
CONTEXT := .

.PHONY: build rebuild pre-build clean-artifacts test

pre-build:
	@echo ">> Copying gemini-toolbox script..."
	cp ../../bin/gemini-toolbox .

clean-artifacts:
	@echo ">> Cleaning artifacts..."
	rm -f gemini-toolbox

build: pre-build
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKER_FILE) .
	$(MAKE) clean-artifacts

rebuild: pre-build
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKER_FILE) .
	$(MAKE) clean-artifacts

print-tag:
	@echo $(IMAGE_TAG)

print-image:
	@echo $(IMAGE_NAME):$(IMAGE_TAG)

test:
	@echo ">> Running Gemini Hub Tests..."
	docker build -t $(IMAGE_NAME)-test -f tests/Dockerfile .
	docker run --rm $(IMAGE_NAME)-test

scan:
	@echo ">> Scanning $(IMAGE_NAME):$(IMAGE_TAG)..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed $(IMAGE_NAME):$(IMAGE_TAG)

ci: rebuild
