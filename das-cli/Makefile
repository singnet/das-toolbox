#!/usr/bin/make -f
LINT_TARGETS=./src
TEMP_DIR := /tmp

debian_changelog:
ifndef DAS_CLI_VERSION
	$(error The DAS_CLI_VERSION environment variable is not defined. Please define it before continuing.)
endif

	./scripts/debian_changelog.sh "$(DAS_CLI_VERSION)"

build: docker-build
	@docker run --rm \
		-e UID=$(shell id -u) \
		-e GID=$(shell id -g) \
		-v "$(CURDIR)/dist:/app/das/dist" \
		-e DAS_CLI_VERSION=$(DAS_CLI_VERSION) \
		das-cli:latest

docker-build-jupyter-notebook:
	@docker build -f .docker/Dockerfile.jupyter-notebook -t trueagi/das:latest-jupyter-notebook .

docker-build: 
	@docker build -f .docker/Dockerfile.das-toolbox -t das-cli:latest .

local-build: debian_changelog
	export TMPDIR=$(TEMP_DIR) && dpkg-buildpackage -us -uc -b -d
man_pages:
	@python3 src/setup.py --command-packages=click_man.commands man_pages --target $(CURDIR)/man

integration_tests:
ifdef DAS_CLI_TEST_CLUSTER
	@bats tests/integration/*.bats --filter-tags 'cluster'
endif

	@bats tests/integration/*.bats --filter-tags '!cluster'

docker-build-ci:
	@docker build -f .docker/Dockerfile.ci -t das-cli-runner:latest .

tests-all: docker-build-ci
	@docker run --privileged --rm das-cli-runner:latest integration_tests

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
