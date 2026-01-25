IMAGE_NAME := gemini-cli-toolbox/hub
DOCKER_FILE := Dockerfile
CONTEXT := .

.PHONY: build rebuild

build:
	docker build -t $(IMAGE_NAME):latest -f $(DOCKER_FILE) $(CONTEXT)

rebuild:
	docker build --no-cache -t $(IMAGE_NAME):latest -f $(DOCKER_FILE) $(CONTEXT)
