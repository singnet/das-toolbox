#!/usr/local/bin/bats

skip "Skip test causing failure for subsequent tests"

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

bats_require_minimum_version 1.5.0

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
    run das-cli update-version

    assert_output "This command is not being executed with sudo."
}

@test "Update package version" {
    local expected_output
    local new_version="0.4.7"
    local current_version="$(get_das_cli_version)"

    run sudo das-cli update-version --version $new_version

    assert_output "Updating the package das-cli...
Package version successfully updated  $current_version --> $new_version."
}

@test "Update package version to the latest" {
    local current_version="$(get_das_cli_version)"
    local latest_version="$(get_das_cli_latest_version das-cli)"

    run sudo das-cli update-version

    assert_output "Updating the package das-cli...
Package version successfully updated  $current_version --> $latest_version."
}

@test "Trying to install invalid version" {
    local version="invalid-version"

    run sudo das-cli update-version --version $version

    assert_output "Updating the package das-cli...
The das-cli could not be updated. Please check if the specified version exists."
}

@test "Trying to update das-cli before it's installed" {
    apt -y remove --autoremove --purge das-cli

    run -127 das-cli update-version

    assert_failure
}
