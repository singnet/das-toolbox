#!/usr/bin/make -f
LINT_TARGETS=./src

debian_changelog:
ifndef DAS_CLI_VERSION
	$(error The DAS_CLI_VERSION environment variable is not defined. Please define it before continuing.)
endif

	./scripts/debian_changelog.sh "$(DAS_CLI_VERSION)"

build: docker-build
	@docker run --rm -v "$(CURDIR)/dist/":/app/das/dist -e DAS_CLI_VERSION=$(DAS_CLI_VERSION) das-cli:latest

docker-build-jupyter-notebook:
	@docker build -f .docker/Dockerfile.jupyter-notebook -t trueagi/das:latest-jupyter-notebook .

docker-build: 
	@docker build -f .docker/Dockerfile.das-toolbox -t das-cli:latest .

local-build: debian_changelog
	dpkg-buildpackage

man_pages:
	@python3 src/setup.py --command-packages=click_man.commands man_pages --target $(CURDIR)/man

integration_tests:
ifdef DAS_CLI_TEST_CLUSTER
	@bats tests/integration/*.bats --filter-tags 'cluster'
endif

	@bats tests/integration/*.bats --filter-tags '!cluster'

isort:
	@isort --settings-path ./src/.isort.cfg $(LINT_TARGETS)

black:
	@black --config ./src/.black.cfg $(LINT_TARGETS)

flake8:
	@flake8 --config ./src/.flake8.cfg $(LINT_TARGETS)

mypy:
	@mypy ./src

lint: isort black flake8 mypy

pre-commit: lint
