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
		-v "$(CURDIR)/dist:/app/das/dist" \
		-v $(TEMP_DIR):$(TEMP_DIR) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		-v /etc/shadow:/etc/shadow:ro \
		-v /etc/gshadow:/etc/gshadow:ro \
		-e USER=$(shell id -u -n) \
		-e PACKAGE_VERSION=$(PACKAGE_VERSION) \
		das-toolbox-package:latest


build-local: debian-changelog
	export TMPDIR=$(TEMP_DIR) && cd pkg && dpkg-buildpackage -us -uc -b -d
