#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    if [ "$current_user" == "root" ]; then
        apt -y update
        apt -y install --allow-downgrades das-cli=0.2.17
    fi
}

teardown() {
    if [ "$current_user" == "root" ]; then
        apt -y remove --autoremove --purge das-cli
    fi
}

@test "Trying to update package version without sudo" {

    if [ "$current_user" == "root" ]; then
        skip
    else
        run das-cli update-version

        assert_output "[31m[PermissionError] This command is not being executed with sudo.[39m"
    fi
}

@test "Update package version" {
    local expected_output
    local new_version="0.2.19"
    local current_version="$(get_das_cli_version)"

    run das-cli update-version --version $new_version

    if [ "$current_user" == "root" ]; then
        assert_output "Updating the package das-cli...
Package version successfully updated  $current_version --> $new_version."
    else
        skip
    fi
}

@test "Update package version to the latest" {
    local current_version="$(get_das_cli_version)"
    local latest_version="$(get_das_cli_latest_version das-cli)"

    if [ "$current_user" == "root" ]; then
        run das-cli update-version

        assert_output "Updating the package das-cli...
Package version successfully updated  $current_version --> $latest_version."
    else
        skip
    fi
}

@test "Trying to install invalid version" {
    local version="invalid-version"

    if [ "$current_user" == "root" ]; then
        run das-cli update-version --version $version

        assert_output "Updating the package das-cli...
The das-cli could not be updated. Please check if the specified version exists."
    else
        skip
    fi
}

@test "Trying to update das-cli before it's installed" {
    if [ "$current_user" == "root" ]; then
        apt -y remove --autoremove --purge das-cli

        run -127 das-cli update-version

        assert_failure
    else
        skip
    fi
}
