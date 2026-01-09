docker-build:
	@docker build -f .docker/Dockerfile.das-runner-manager -t das-runner-manager:latest .

build: build-das-runner-manager-agent-image docker-build
	@docker run --rm \
		--user "$(shell id -u):$(shell id -g)" \
		-v "$(shell pwd)/dist:/app/das/dist" \
		-v "$(shell pwd):/app/das" \
		-v "/etc/passwd:/etc/passwd:ro" \
		-v "/etc/group:/etc/group:ro" \
		-v "/etc/shadow:/etc/shadow:ro" \
		-v "/etc/gshadow:/etc/gshadow:ro" \
		das-runner-manager:latest

build-github-runner-image:
	@docker build -f .docker/Dockerfile.github-runner -t levisingnet/github-runner:ubuntu-22.04 .

build-das-runner-manager-agent-image:
	@docker build -f .docker/Dockerfile.das-runner-manager-agent -t levisingnet/das-runner-manager-agent:latest .

run-volume-cleaner:
	@./scripts/clean_runner_volume.sh

setup-cron-job:
	@(crontab -l 2>/dev/null; echo "0 3 * * 6 $$(pwd)/scripts/clean_runner_volume.sh") | crontab -

remove-cron-job:
	@(crontab -l 2>/dev/null | grep -v "clean_runner_volume.sh") | crontab -