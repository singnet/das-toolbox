#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"
}

function ensure_env() {
    mkdir -p "${das_config_dir}"
    echo "configpath=${das_config_file}" > "${das_env_file}"
}

@test "listing config with unset configuration file" {
    unset_config

    run das-cli config list

    assert_output --partial "[FileNotFoundError]"
}

@test "listing config with valid configuration file" {
    use_config "simple"
    ensure_env

    run das-cli config list

    assert_output --partial "localhost:40020"
    assert_output --partial "localhost:40021"
    assert_output --partial "localhost:40002"
    assert_output --partial "localhost:40019"
}

@test "get_config reads values from file correctly" {
    use_config "simple"

    run get_config ".atomdb.redis.endpoint"
    assert_output "localhost:40020"

    run get_config ".environment.jupyter.endpoint"
    assert_output "localhost:40019"
}

@test "config file can be modified programmatically" {
    use_config "simple"

    update_json_key "$das_config_file" atomdb.redis.endpoint "localhost:9999"

    run get_config ".atomdb.redis.endpoint"
    assert_output "localhost:9999"
}

@test "raises error when config file is missing but env exists" {
    use_config "simple"
    ensure_env

    rm -f "$das_config_file"

    run das-cli config list

    assert_output --partial "[FileNotFoundError]"
}

@test "raises error when schema version is invalid" {
    use_config "simple"
    ensure_env

    update_json_key "$das_config_file" schema_version "2.0"

    run das-cli config list

    assert_output --partial "[ValueError]"
}

@test "use_config correctly sets env and file" {
    use_config "simple"

    [ -f "$das_config_file" ]
    [ -f "$das_env_file" ]

    run cat "$das_env_file"
    assert_output "configpath=${das_config_file}"
}