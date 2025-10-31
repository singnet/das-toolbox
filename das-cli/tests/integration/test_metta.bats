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
    assert_line --partial "Checking syntax... OK"
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

@test "Loading a MeTTa file with a relative path" {
    local metta_file_path="$(realpath --relative-to="$BATS_TEST_DIRNAME/../.." "$test_fixtures_dir/metta/animals.metta")"
    local mongodb_port="$(get_config .services.mongodb.port)"
    local redis_port="$(get_config .services.redis.port)"

    das-cli db start

    sleep 20s

    run das-cli metta load $metta_file_path

    assert_failure
    assert_line --partial "The path must be absolute."
}

@test "Loading an invalid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/invalid.metta"
    local mongodb_port="$(get_config .services.mongodb.port)"
    local redis_port="$(get_config .services.redis.port)"

    das-cli db start

    sleep 20s

    run das-cli metta load $metta_file_path


    assert_line --partial "das-cli-redis-$redis_port is running on port $redis_port"
    assert_line --partial "das-cli-mongodb-$mongodb_port is running on port $mongodb_port"
    assert_line --partial "Loading metta file $metta_file_path..."
    assert_line --partial "[31m[DockerError] File 'invalid.metta' could not be loaded.[39m"
}

@test "Loading a MeTTa file without read permission" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    chmod -r "$metta_file_path"

    run das-cli metta load "$metta_file_path"

    assert_line --partial "Error: Invalid value for 'PATH': Path '$metta_file_path' is not readable."

    chmod +r "$metta_file_path"
}

@test "Loading a valid MeTTa file" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"
    local mongodb_port="$(get_config .services.mongodb.port)"
    local redis_port="$(get_config .services.redis.port)"

    das-cli db start

    sleep 20s

    run das-cli metta load $metta_file_path

    assert_line --partial "das-cli-redis-$redis_port is running on port $redis_port"
    assert_line --partial "das-cli-mongodb-$mongodb_port is running on port $mongodb_port"
    assert_line --partial "Loading metta file ${metta_file_path}..."
    assert_line --partial "Done."
    assert_success
}

@test "Loading directory with MeTTa files" {
    local metta_file_path="$test_fixtures_dir/metta"
    local mongodb_port="$(get_config .services.mongodb.port)"
    local redis_port="$(get_config .services.redis.port)"

    das-cli db start

    sleep 20s

    run das-cli metta load $metta_file_path

    assert_line --partial "das-cli-redis-$redis_port is running on port $redis_port"
    assert_line --partial "das-cli-mongodb-$mongodb_port is running on port $mongodb_port"
    assert_line --partial "Loading metta file ${metta_file_path}/animals.metta..."
    assert_line --partial "Loading metta file ${metta_file_path}/invalid.metta..."
    assert_line --partial "Done."
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
    local mongodb_port="$(get_config .services.mongodb.port)"
    local redis_port="$(get_config .services.redis.port)"

    das-cli db stop

    run das-cli metta load $metta_file_path

    assert_line --partial "das-cli-redis-$redis_port is not running on port ${redis_port}"
    assert_line --partial "das-cli-mongodb-$mongodb_port is not running on port ${mongodb_port}"

    assert_line --partial "Please use 'db start' to start required services before running 'metta load'."
}
