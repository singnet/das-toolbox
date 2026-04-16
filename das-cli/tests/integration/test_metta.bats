#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/errors'

setup() {
    use_config "simple"
    das-cli db start
}

@test "Checking MeTTa file syntax with unset configuration file" {
    unset_config

    run das-cli metta check "$test_fixtures_dir/metta/animals.metta"

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Checking syntax of a valid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    run das-cli metta check "$metta_file_path"

    assert_line --partial "$metta_file_path"
    assert_line --partial "Checking syntax... OK"
}

@test "Checking syntax of an invalid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/invalid.metta"

    run das-cli metta check "$metta_file_path"

    assert_line --partial "Checking syntax... FAILED"
}

@test "Checking syntax of multiple MeTTa files" {
    local metta_file_path="$test_fixtures_dir/metta/"

    run das-cli metta check "$metta_file_path"

    assert_line --partial "$metta_file_path"
    assert_line --partial "Checking syntax... OK"
    assert_line --partial "Checking syntax... FAILED"
}

@test "Checking MeTTa file with invalid path" {
    run das-cli metta check "/invalid/path"
    assert_failure
}

@test "Checking MeTTa file command without path" {
    run das-cli metta check
    assert_failure
}

@test "Loading MeTTa file with unset configuration file" {
    unset_config

    run das-cli metta load "$test_fixtures_dir/metta/animals.metta"

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Loading a MeTTa file with a relative path" {
    local metta_file_path="$(realpath --relative-to="$BATS_TEST_DIRNAME/../.." "$test_fixtures_dir/metta/animals.metta")"

    run das-cli metta load "$metta_file_path"

    assert_failure
    assert_line --partial "The path must be absolute."
}

@test "Loading an invalid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/invalid.metta"

    run das-cli metta load "$metta_file_path"

    assert_line --partial "is running on port"
    assert_line --partial "Loading metta file"
    assert_line --partial "$metta_file_path"
    assert_line --partial "$DOCKER_CONTAINER_MISSING" || true
    assert_line --partial "could not be loaded"
}

@test "Loading a MeTTa file without read permission" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    chmod -r "$metta_file_path"

    run das-cli metta load "$metta_file_path"

    assert_line --partial "not readable"

    chmod +r "$metta_file_path"
}

@test "Loading a valid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    run das-cli metta load "$metta_file_path"

    assert_line --partial "is running on port"
    assert_line --partial "Loading metta file"
    assert_line --partial "$metta_file_path"
    assert_line --partial "Done loading."

    assert_success
}

@test "Loading directory with MeTTa files" {
    local metta_file_path="$test_fixtures_dir/metta"

    run das-cli metta load "$metta_file_path"

    assert_line --partial "Loading metta file"
    assert_line --partial "animals.metta"
    assert_line --partial "invalid.metta"
    assert_line --partial "Done loading."
}

@test "Trying to load a MeTTa file with an invalid path" {
    run das-cli metta load "/invalid/path"
    assert_failure
}

@test "Trying to run the load command with a path" {
    run das-cli metta load
    assert_failure
}

@test "Loading MeTTa file before db has being started" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    das-cli db stop

    run das-cli metta load "$metta_file_path"

    assert_line --partial "is not running on port"
    assert_line --partial "Please use 'db start'"
}