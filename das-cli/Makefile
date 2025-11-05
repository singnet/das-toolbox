#!/usr/bin/make -f

LINT_TARGETS = ./src

tests-local:
ifeq ($(strip $(NAME)),)
ifeq ($(strip $(DAS_CLI_TEST_CLUSTER)),)
	@echo "Running integration tests..."
	@bats tests/integration/*.bats --filter-tags '!cluster'
else
	@echo "Running cluster integration tests..."
	@bats tests/integration/*.bats --filter-tags 'cluster'
endif
else
	@echo "Running integration test: $(NAME)"
	@bats tests/integration/$(NAME)
	@echo "Test $(NAME) completed"
endif

docker-build-test:
	@echo "Building Docker test image..."
	@docker build -f Dockerfile.test -t das-cli-runner:latest .


tests-all: docker-build-test
	@echo "Running all integration tests in Docker..."
	@docker run --privileged --rm das-cli-runner:latest tests-local

isort:
	@echo "Sorting imports with isort..."
	@isort --settings-path ./src/.isort.cfg $(LINT_TARGETS)

black:
	@echo "Formatting code with black..."
	@black --config ./src/.black.cfg $(LINT_TARGETS)

flake8:
	@echo "Checking code style with flake8..."
	@flake8 --config ./src/.flake8.cfg $(LINT_TARGETS)

mypy:
	@echo "Running type checks with mypy..."
	@mypy --config-file src/mypy.ini $(LINT_TARGETS)

lint: isort black flake8 mypy
	@echo "All linters passed successfully."


pre-commit: lint
	@echo "Pre-commit checks completed successfully."


help:
	@echo ""
	@echo "Available targets:"
	@echo "  tests-local [NAME=<test>] [DAS_CLI_TEST_CLUSTER=1]   Run local integration tests"
	@echo "  tests-all                                            Run all integration tests in Docker"
	@echo "  lint                                                 Run all linters (isort, black, flake8, mypy)"
	@echo "  pre-commit                                           Run all pre-commit checks"
	@echo ""

DEFAULT := help