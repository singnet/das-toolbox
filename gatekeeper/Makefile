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

deb-package-builder:
	@docker build -f .docker/Dockerfile.package -t package-builder:latest .


build: build-agent build-api build-cli deb-package-builder
	@docker run --rm \
	-v "$(shell pwd)/agent/bin/agent:/workspace/usr/bin/gk-port-watcher" \
	-v "$(shell pwd)/api/bin/api:/workspace/usr/bin/gk-server" \
	-v "$(shell pwd)/cli/bin/cli:/workspace/usr/bin/gkctl" \
	-v "$(shell pwd)/build:/workspace/build" \
	package-builder:latest