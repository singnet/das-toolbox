#!/usr/bin/make -f

TEMP_DIR := /tmp

debian-changelog:
ifndef PACKAGE_VERSION
	$(error The PACKAGE_VERSION environment variable is not defined. Please define it before continuing.)
endif

	@bash -x ./scripts/gen-debian-changelog.sh "$(PACKAGE_VERSION)" "$(CURDIR)/pkg"

docker-build:
	@docker build -t das-toolbox-package:latest .


build: docker-build
	@docker run --rm \
		-e UID=$(shell id -u) \
		-e GID=$(shell id -g) \
		-v "$(CURDIR)/dist:/app/das/dist" \
		-e PACKAGE_VERSION=$(PACKAGE_VERSION) \
		das-toolbox-package:latest


build-local: debian-changelog
	export TMPDIR=$(TEMP_DIR) && cd pkg && dpkg-buildpackage -us -uc -b -d
