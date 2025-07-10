#!/usr/bin/make -f

LINT_TARGETS=./src

tests-local:
ifdef DAS_CLI_TEST_CLUSTER
	@bats tests/integration/*.bats --filter-tags 'cluster'
endif

	@bats tests/integration/test_link_creation_agent.bats --filter-tags '!cluster'

docker-build-test:
	@docker build -f Dockerfile.test -t das-cli-runner:latest .

tests-all: docker-build-test
	@docker run --privileged --rm das-cli-runner:latest tests-local

isort:
	@isort --settings-path ./src/.isort.cfg $(LINT_TARGETS)

black:
	@black --config ./src/.black.cfg $(LINT_TARGETS)

flake8:
	@flake8 --config ./src/.flake8.cfg $(LINT_TARGETS)

mypy:
	@mypy --config-file src/mypy.ini ./src

lint: isort black flake8 mypy

pre-commit: lint
