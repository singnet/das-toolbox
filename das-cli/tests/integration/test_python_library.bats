#!/usr/local/bin/bats

skip "Tests skipped: required package 'hyperon-das-atomdb' is unavailable. We're facing issues due to missing hyperon-das-atomdb packages, blocking test execution."

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    libs=(hyperon-das hyperon-das-atomdb)

    pip3 install hyperon-das==0.7.13
}

teardown() {
    pip3 uninstall -y hyperon-das
    pip3 uninstall -y hyperon-das-atomdb
}

@test "Listing all python library versions" {
    local available_versions_regex="^.*\savailable\sversions:"

    run das-cli python-library list

    local available_versions_match_count=$(echo "$output" | grep -cE $available_versions_regex)

    assert_output --regexp $available_versions_regex
    assert [ "$available_versions_match_count" -eq "${#libs[@]}" ]
}

@test "Show available python library versions" {
    local available_versions_regex="^.*\savailable\sversions:"

    for lib in "${libs[@]}"; do
        run das-cli python-library list --library $lib

        local available_versions_match_count=$(echo "$output" | grep -cE $available_versions_regex)

        assert_output --regexp $available_versions_regex
        assert [ "$available_versions_match_count" -eq 1 ]
    done
}

@test "Trying to show version to an invalid python library" {
    local invalid_lib="invalid-python-library"

    run das-cli python-library list --library $invalid_lib

    assert_failure
}

@test "Set python library to a version" {
    local new_version="0.4.0"

    local current_hyperon_das_version="$(get_python_package_version hyperon-das)"
    local current_hyperon_das_atomdb_version="$(get_python_package_version hyperon-das-atomdb)"

    local latest_hyperon_das_version="$(get_python_package_latest_version hyperon-das)"
    local latest_hyperon_das_atomdb_version="$(get_python_package_latest_version hyperon-das-atomdb)"

    run das-cli python-library set --hyperon-das $new_version --hyperon-das-atomdb $new_version

    assert_output "Updating package hyperon-das...
Package hyperon-das has been successfully updated.
Updating package hyperon-das-atomdb...
Package hyperon-das-atomdb has been successfully updated.
All package has been successfully updated.
hyperon-das
  INSTALLED: $new_version
  LATEST:    $latest_hyperon_das_version
hyperon-das-atomdb
  INSTALLED: $new_version
  LATEST:    $latest_hyperon_das_atomdb_version"

}

@test "Trying to set a newer version without specifing the library" {

    run das-cli python-library set

    assert_output "At least one of --hyperon-das or --hyperon-das-atomdb must be provided."

}

@test "Trying to set python libraries with invalid version" {

    run das-cli python-library set --hyperon-das 0.0.0

    assert_output "Updating package hyperon-das...
Failed to update package hyperon-das. Please verify if the provided version exists or ensure the package name is correct.
One or more packages could not be updated."
}

@test "Update library versions to latest version" {
    local latest_hyperon_das_version="$(get_python_package_latest_version hyperon-das)"
    local latest_hyperon_das_atomdb_version="$(get_python_package_latest_version hyperon-das-atomdb)"

    run das-cli python-library update

    assert_output "Updating package hyperon-das...
Updating package hyperon-das-atomdb...
All package has been successfully updated.
hyperon-das
  INSTALLED: $latest_hyperon_das_version
  LATEST:    $latest_hyperon_das_version
hyperon-das-atomdb
  INSTALLED: $latest_hyperon_das_atomdb_version
  LATEST:    $latest_hyperon_das_atomdb_version"
}

@test "Trying to update library version before install library" {
    pip3 uninstall -y hyperon-das
    pip3 uninstall -y hyperon-das-atomdb

    run das-cli python-library update

    assert_output "Updating package hyperon-das...
Package 'hyperon-das' is not installed.
Updating package hyperon-das-atomdb...
Package 'hyperon-das-atomdb' is not installed.
One or more packages could not be updated."
}

@test "Showing currently installed version of libraries" {
    local current_hyperon_das_version="$(get_python_package_version hyperon-das)"
    local current_hyperon_das_atomdb_version="$(get_python_package_version hyperon-das-atomdb)"

    local latest_hyperon_das_version="$(get_python_package_latest_version hyperon-das)"
    local latest_hyperon_das_atomdb_version="$(get_python_package_latest_version hyperon-das-atomdb)"

    run das-cli python-library version

    assert_output "hyperon-das
  INSTALLED: $current_hyperon_das_version
  LATEST:    $latest_hyperon_das_version
hyperon-das-atomdb
  INSTALLED: $current_hyperon_das_atomdb_version
  LATEST:    $latest_hyperon_das_atomdb_version"
}

@test "Trying to show currently installed version of library before installing it" {
    pip3 uninstall -y hyperon-das

    run das-cli python-library version

    assert_output "[31m[PackageNotFoundError] Package 'hyperon-das' is not installed.[39m"
}
