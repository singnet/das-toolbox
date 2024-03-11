#!/usr/bin/make -f

debian_changelog:
	ifndef DAS_CLI_VERSION
		$(error The DAS_CLI_VERSION environment variable is not defined. Please define it before continuing.)
	endif

	./scripts/debian_changelog.sh "$(DAS_CLI_VERSION)"

build: debian_changelog
	dpkg-buildpackage