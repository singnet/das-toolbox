agent-builder:
	@docker build -f .docker/Dockerfile.binary --build-arg EXEC_NAME=agent -t agent-builder:latest ./agent

build-agent: agent-builder
	@docker run --rm \
	-v "$(shell pwd)/agent:/app/" \
	agent-builder:latest

