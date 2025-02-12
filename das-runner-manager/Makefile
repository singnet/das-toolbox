docker-build:
	@docker build -f .docker/Dockerfile.das-runner-manager -t das-runner-manager:latest .

build: docker-build
	@docker run --rm -v "$(CURDIR)/dist/":/app/das/dist das-runner-manager:latest

build-github-runner-image:
	@docker build -f .docker/Dockerfile.github-runner -t levisingnet/github-runner:ubuntu-22.04 .


