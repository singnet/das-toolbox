#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

bats_require_minimum_version 1.5.0

PACKAGE_NAME="das-toolbox"

setup() {
    restore_package=0
    original_version=""
    original_deb=""

    if _is_package_installed; then
        original_version="$(_package_version)"
    fi
    original_deb="$(_dist_deb)"
}

teardown() {
    if [ "${restore_package:-0}" -eq 1 ]; then
        _restore_das_toolbox
    fi
}

_is_package_installed() {
    dpkg-query -W -f='${Status}' "$PACKAGE_NAME" 2>/dev/null | grep -q 'install ok installed'
}

_package_version() {
    dpkg-query -W -f='${Version}' "$PACKAGE_NAME" 2>/dev/null
}

_dist_deb() {
    find "${BATS_TEST_DIRNAME}/../../../dist" -name '*.deb' -type f 2>/dev/null | head -n 1
}

_require_passwordless_sudo() {
    if ! command -v sudo >/dev/null; then
        skip "sudo is not available"
    fi
    if ! sudo -n true 2>/dev/null; then
        skip "passwordless sudo is not available"
    fi
}

_require_apt_package() {
    if ! _is_package_installed; then
        skip "das-toolbox is not installed via APT"
    fi
}

_alternate_apt_version() {
    local current="$1"
    apt-cache madison "$PACKAGE_NAME" 2>/dev/null | awk '{print $3}' | grep -vxF "$current" | head -n 1
}

_candidate_apt_version() {
    apt-cache policy "$PACKAGE_NAME" 2>/dev/null | awk '/Candidate:/ {print $2; exit}'
}

_restore_das_toolbox() {
    if [ -n "${original_deb:-}" ] && [ -f "${original_deb}" ]; then
        sudo -n apt -y --allow-downgrades install "$original_deb"
        return
    fi
    if [ -n "${original_version:-}" ]; then
        sudo -n apt -y --allow-downgrades install "${PACKAGE_NAME}=${original_version}"
    fi
}

@test "Trying to update package version without sudo" {
    if [ -n "${SUDO_USER:-}" ] || [ "$(id -u)" -eq 0 ]; then
        skip "Cannot assert the non-sudo path when already running with root privileges"
    fi

    run das-cli update-version
    assert_failure
    assert_output --partial "Requires 'root' permissions to execute"
}

@test "Update package version" {
    _require_passwordless_sudo
    _require_apt_package

    local current_version new_version
    current_version="$(_package_version)"
    new_version="$(_alternate_apt_version "$current_version")"

    if [ -z "$new_version" ]; then
        skip "no alternate das-toolbox version available in apt"
    fi

    restore_package=1

    run sudo das-cli update-version --version "$new_version"

    assert_success
    assert_output --partial "Updating the package das-toolbox..."
    assert_output --partial "Package version successfully updated  ${current_version} --> ${new_version}."
}

@test "Update package version to the latest" {
    _require_passwordless_sudo
    _require_apt_package

    local current_version latest_version
    current_version="$(_package_version)"
    latest_version="$(_candidate_apt_version)"

    if [ -z "$latest_version" ] || [ "$latest_version" = "(none)" ]; then
        skip "no das-toolbox candidate version available in apt"
    fi

    restore_package=1

    run sudo das-cli update-version

    assert_success
    assert_output --partial "Updating the package das-toolbox..."
    if [ "$current_version" = "$latest_version" ]; then
        assert_output --partial "The package is already updated to version ${latest_version}."
    else
        assert_output --partial "Package version successfully updated  ${current_version} --> ${latest_version}."
    fi
}

@test "Trying to install invalid version" {
    _require_passwordless_sudo
    _require_apt_package

    local version="invalid-version"

    run sudo das-cli update-version --version $version

    assert_failure
    assert_output --partial "Updating the package das-toolbox..."
    assert_output --partial "could not be updated"
}

@test "Trying to update das-toolbox before it's installed" {
    _require_passwordless_sudo
    _require_apt_package

    local cli_copy
    cli_copy="${BATS_TEST_TMPDIR}/das-cli"
    cp "$(command -v das-cli)" "$cli_copy"
    chmod +x "$cli_copy"

    restore_package=1
    sudo -n apt -y remove "$PACKAGE_NAME"

    run sudo "$cli_copy" update-version

    assert_failure
    assert_output --partial "The package 'das-toolbox' is not installed via APT."
}
