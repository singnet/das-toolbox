agent-builder:
	@docker build -f .docker/Dockerfile.binary --build-arg EXEC_NAME=agent -t agent-builder:latest ./agent

build-agent: agent-builder
	@docker run --rm \
	-v "$(shell pwd)/agent:/app/" \
	agent-builder:latest

api-builder:
	@docker build -f .docker/Dockerfile.binary --build-arg EXEC_NAME=api -t api-builder:latest ./api

build-api: api-builder
	@docker run --rm \
	-v "$(shell pwd)/api:/app/" \
	api-builder:latest

cli-builder:
	@docker build -f .docker/Dockerfile.binary --build-arg EXEC_NAME=cli -t cli-builder:latest ./cli

build-cli: cli-builder
	@docker run --rm \
	-v "$(shell pwd)/cli:/app/" \
	cli-builder:latest

build: build-agent build-api build-cli
