#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
  if [ -z "${REMOTE_HOST+x}" ]; then
    skip "Environment variable REMOTE_HOST is not set. Skipping all tests in this file."
  fi

  libs=(hyperon-das hyperon-das-atomdb)

  pip3 install hyperon-das==0.7.13
}

teardown() {
  pip3 uninstall -y hyperon-das
  pip3 uninstall -y hyperon-das-atomdb
}

@test "Listing all python library versions" {
  local available_versions_regex="^.*\savailable\sversions:"
  local available_versions_match_count

  run python3 src/das_cli.py python-library list --remote --host $REMOTE_HOST

  available_versions_match_count=$(echo "$output" | grep -cE "$available_versions_regex")

  assert_output --regexp "$available_versions_regex"
  assert [ "$available_versions_match_count" -eq "${#libs[@]}" ]
}

@test "Show available python library versions" {
  local available_versions_regex="^.*\savailable\sversions:"

  for lib in "${libs[@]}"; do
    local available_versions_match_count

    run python3 src/das_cli.py python-library list --library "$lib" --remote --host $REMOTE_HOST
    available_versions_match_count=$(echo "$output" | grep -cE "$available_versions_regex")

    assert_output --regexp "$available_versions_regex"
    assert [ "$available_versions_match_count" -eq 1 ]
  done
}

@test "Trying to show version to an invalid python library" {
  local invalid_lib="invalid-python-library"

  run python3 src/das_cli.py python-library list --library $invalid_lib --remote --host $REMOTE_HOST

  assert_failure
}
