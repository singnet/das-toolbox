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
    root_cfg_existed=0
    root_env_existed=0
    root_cfg_backup=""
    root_env_backup=""
    root_state_touched=0

    if _is_package_installed; then
        original_version="$(_package_version)"
        if ! original_deb="$(_matching_dist_deb "$original_version")"; then
            original_deb=""
        fi
    fi
}

teardown() {
    if [ "${restore_package:-0}" -eq 1 ]; then
        _restore_das_toolbox
    fi

    if [ "${root_state_touched:-0}" -eq 1 ]; then
        _restore_root_state
    fi
}

_is_package_installed() {
    dpkg-query -W -f='${Status}' "$PACKAGE_NAME" 2>/dev/null | grep -q 'install ok installed'
}

_package_version() {
    dpkg-query -W -f='${Version}' "$PACKAGE_NAME" 2>/dev/null
}

_matching_dist_deb() {
    local expected_version="$1"
    local dist_dir="${BATS_TEST_DIRNAME}/../../../dist"
    local deb pkg ver

    [ -n "$expected_version" ] || return 1
    [ -d "$dist_dir" ] || return 1

    while IFS= read -r -d '' deb; do
        pkg="$(dpkg-deb -f "$deb" Package 2>/dev/null)" || continue
        ver="$(dpkg-deb -f "$deb" Version 2>/dev/null)" || continue
        if [ "$pkg" = "$PACKAGE_NAME" ] && [ "$ver" = "$expected_version" ]; then
            printf '%s\n' "$deb"
            return 0
        fi
    done < <(find "$dist_dir" -name '*.deb' -type f -print0 2>/dev/null)

    return 1
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
    if [ -z "${original_version:-}" ]; then
        return
    fi

    if [ -n "${original_deb:-}" ] && [ -f "${original_deb}" ]; then
        if sudo -n apt -y --allow-downgrades install "$original_deb"; then
            return
        fi
    fi

    sudo -n apt -y --allow-downgrades install "${PACKAGE_NAME}=${original_version}"
}

_backup_root_state() {
    root_state_touched=1
    root_cfg_backup="${BATS_TEST_TMPDIR}/root-config.backup.json"
    root_env_backup="${BATS_TEST_TMPDIR}/root-env.backup"

    if sudo -n test -f /root/.das/config.json; then
        root_cfg_existed=1
        sudo -n cat /root/.das/config.json > "$root_cfg_backup"
    fi

    if sudo -n test -f /root/.das/.env; then
        root_env_existed=1
        sudo -n cat /root/.das/.env > "$root_env_backup"
    fi
}

_restore_root_state() {
    if [ "${root_cfg_existed:-0}" -eq 1 ] && [ -f "${root_cfg_backup:-}" ]; then
        sudo -n install -D -m 0644 "$root_cfg_backup" /root/.das/config.json
    else
        sudo -n rm -f /root/.das/config.json
    fi

    if [ "${root_env_existed:-0}" -eq 1 ] && [ -f "${root_env_backup:-}" ]; then
        sudo -n install -D -m 0644 "$root_env_backup" /root/.das/.env
    else
        sudo -n rm -f /root/.das/.env
    fi
}

_provision_root_runtime_config() {
    local source_config="${BATS_TEST_DIRNAME}/fixtures/config/simple.json"

    _backup_root_state

    sudo -n mkdir -p /root/.das
    sudo -n install -m 0644 "$source_config" /root/.das/config.json
    printf 'configpath=/root/.das/config.json\n' | sudo -n tee /root/.das/.env >/dev/null
}

_clear_root_runtime_config() {
    _backup_root_state

    sudo -n rm -f /root/.das/config.json /root/.das/.env
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

    _provision_root_runtime_config

    run sudo "$cli_copy" update-version

    assert_failure
    assert_output --partial "The package 'das-toolbox' is not installed via APT."
}

@test "Trying to update das-toolbox before it's installed without default config file" {
    _require_passwordless_sudo
    _require_apt_package

    local cli_copy
    cli_copy="${BATS_TEST_TMPDIR}/das-cli"
    cp "$(command -v das-cli)" "$cli_copy"
    chmod +x "$cli_copy"

    restore_package=1
    sudo -n apt -y remove "$PACKAGE_NAME"

    _clear_root_runtime_config

    run sudo "$cli_copy" update-version

    assert_failure
    assert_output --partial "Default config file not found"
}
