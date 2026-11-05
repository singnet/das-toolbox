#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
  if [ -z "${REMOTE_HOST+x}" ]; then
    skip "Environment variable REMOTE_HOST is not set. Skipping all tests in this file."
  fi

  if [[ "$BATS_TEST_DESCRIPTION" == "Remote argument quoting "* ]]; then
    remote_test_dir="$(mktemp -d)" || return 1
    return 0
  fi

  libs=(hyperon-das hyperon-das-atomdb)

  libraries_installed=1
  pip3 install hyperon-das==0.7.13
}

teardown() {
  if [[ -n "${remote_test_dir:-}" ]]; then
    rm -rf "$remote_test_dir"
  fi
  if [[ "${libraries_installed:-}" != 1 ]]; then
    return 0
  fi
  pip3 uninstall -y hyperon-das
  pip3 uninstall -y hyperon-das-atomdb
}

remote_config_list() {
  das-cli config list "$1" --remote --host "$REMOTE_HOST" -o json \
    > "$remote_test_dir/result.json" 2> "$remote_test_dir/stderr"
}

@test "Remote argument quoting preserves positional values without shell expansion" {
  local value
  local values=(
    'missing key with spaces'
    '$HOME'
    '$(printf expanded)'
    '`printf expanded`'
    'missing; printf expanded #'
    "missing 'single' and \"double\" quotes"
    'missing * ? [abc]'
    $'missing\nsecond line'
  )

  for value in "${values[@]}"; do
    run remote_config_list "$value"
    assert_failure

    run jq -r '.key' "$remote_test_dir/result.json"
    assert_success
    assert_output "$value"

    run jq -r '.status' "$remote_test_dir/result.json"
    assert_success
    assert_output "error"
  done
}

@test "Remote argument quoting preserves file option values without shell expansion" {
  local value
  local file_path
  local values=(
    'file with spaces.json'
    'file-$HOME.json'
    'file-$(printf expanded).json'
    'file-`printf expanded`.json'
    'file; printf expanded #.json'
    'file-*.json'
  )

  for value in "${values[@]}"; do
    file_path="/das-remote-quoting-missing-$$-${BATS_TEST_NUMBER}/${value}"
    run das-cli config set --file "$file_path" --remote --host "$REMOTE_HOST" -o json
    assert_failure
    assert_output --partial "Error: Invalid value for '--file': File '${file_path}' does not exist."
  done
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
