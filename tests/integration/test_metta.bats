#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"
}

teardown() {
    das-cli db stop
}

@test "Checking MeTTa file syntax with unset configuration file" {
    unset_config

    run das-cli metta check "$test_fixtures_dir/metta/animals.metta"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Checking syntax of a valid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    run das-cli metta check $metta_file_path

    assert_line --partial $metta_file_path
    assert_line --partial "Syntax check OK"
}

@test "Checking syntax of an invalid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/invalid.metta"

    run das-cli metta check $metta_file_path

    assert_line --partial $metta_file_path
    assert_line --partial "syntax error"
}

@test "Checking syntax of multiple MeTTa files" {
    local metta_file_path="$test_fixtures_dir/metta/"

    run das-cli metta check $metta_file_path

    assert_line --partial $metta_file_path
    assert_line --partial "Syntax check OK"
    assert_line --partial "syntax error"
}

@test "Checking MeTTa file with invalid path" {
    local metta_file_path="/invalid/path"

    run das-cli metta check $metta_file_path

    assert_failure
}

@test "Checking MeTTa file command without path" {

    run das-cli metta check

    assert_failure
}

@test "Loading MeTTa file with unset configuration file" {
    unset_config

    run das-cli metta load "$test_fixtures_dir/metta/animals.metta"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Loading an invalid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/invalid.metta"
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"

    das-cli db start

    sleep 20s

    run das-cli metta load $metta_file_path

    assert_line --partial "Redis is running on port $redis_port"
    assert_line --partial "MongoDB is running on port $mongodb_port"
    assert_line --partial "Loading metta file(s)..."
    assert_line --partial "[31m[DockerError] File 'invalid.metta' could not be loaded.[39m"
}

@test "Loading a valid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"

    das-cli db start

    sleep 20s

    run das-cli metta load $metta_file_path

    assert_line --partial "Redis is running on port $redis_port"
    assert_line --partial "MongoDB is running on port $mongodb_port"
    assert_line --partial "Loading metta file(s)..."
    assert_line --partial "Done."
    assert_success
}

@test "Trying to load a MeTTa file with an invalid path" {
    local metta_file_path="/invalid/path"

    run das-cli metta load $metta_file_path

    assert_failure
}

@test "Trying to run the load command with a path" {

    run das-cli metta load

    assert_failure
}

@test "Loading MeTTa file before db has being started" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    das-cli db stop

    run das-cli metta load $metta_file_path

    assert_output "Redis is not running
MongoDB is not running
[31m[DockerContainerNotFoundError] 
Please use 'db start' to start required services before running 'metta load'.[39m"
}
