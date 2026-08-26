#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

bats_require_minimum_version 1.5.0

setup() {
    installed_fixture_package=0

    if [ "$current_user" == "root" ]; then
        if ! dpkg-query -W -f='${Status}' das-cli 2>/dev/null | grep -q 'install ok installed'; then
            apt -y update
            apt -y install --allow-downgrades das-cli=0.2.17
            installed_fixture_package=1
        fi
    fi
}

teardown() {
    if [ "${installed_fixture_package:-0}" -eq 1 ]; then
        apt -y remove --autoremove --purge das-cli
    fi
}

@test "Trying to update package version without sudo" {
    if [ -n "${SUDO_USER:-}" ] || [ "$(id -u)" -eq 0 ]; then
        skip "Cannot assert the non-sudo path in this environment"
    fi

    run das-cli update-version
    assert_failure
    assert_output --partial "Requires 'root' permissions to execute"
}

@test "Update package version" {
    skip "Skip test causing failure for subsequent tests"

    local expected_output
    local new_version="0.4.7"
    local current_version="$(get_das_cli_version)"

    run sudo das-cli update-version --version $new_version

    assert_output "Updating the package das-cli...
Package version successfully updated  $current_version --> $new_version."
}

@test "Update package version to the latest" {
    skip "Skip test causing failure for subsequent tests"

    local current_version="$(get_das_cli_version)"
    local latest_version="$(get_das_cli_latest_version das-cli)"

    run sudo das-cli update-version

    assert_output "Updating the package das-cli...
Package version successfully updated  $current_version --> $latest_version."
}

@test "Trying to install invalid version" {
    local version="invalid-version"

    run sudo das-cli update-version --version $version

    assert_failure
    assert_output --partial "Updating the package das-toolbox..."
    assert_output --partial "could not be updated"
}

@test "Trying to update das-cli before it's installed" {
    skip "Skip test causing failure for subsequent tests"

    apt -y remove --autoremove --purge das-cli

    run -127 das-cli update-version

    assert_failure
}
