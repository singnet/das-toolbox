#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/errors'

setup() {
    use_config "simple"
}

ensure_env() {
    mkdir -p "${das_config_dir}"
    echo "configpath=${das_config_file}" > "${das_env_file}"
}

assert_config_core_endpoints() {
    run get_config ".atomdb.redis.endpoint"
    assert_output "localhost:40020"

    run get_config ".atomdb.mongodb.endpoint"
    assert_output "localhost:40021"

    run get_config ".agents.query.endpoint"
    assert_output "localhost:40002"

    run get_config ".environment.jupyter.endpoint"
    assert_output "localhost:40019"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"

    run get_config ".agents.context.endpoint"
    assert_output "localhost:40006"

    run get_config ".agents.atomdb.endpoint"
    assert_output "localhost:40007"

    run get_config ".agents.command_router.endpoint"
    assert_output "localhost:40008"
}

@test "listing config with unset configuration file" {
    unset_config

    run das-cli config list

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "listing config with valid configuration file" {
    use_config "simple"
    ensure_env

    run das-cli config list

    assert_config_core_endpoints
}

@test "get_config reads values from file correctly" {
    use_config "simple"

    run get_config ".atomdb.redis.endpoint"
    assert_output "localhost:40020"

    run get_config ".atomdb.mongodb.endpoint"
    assert_output "localhost:40021"
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

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "use_config correctly sets env and file" {
    use_config "simple"

    [ -f "$das_config_file" ]
    [ -f "$das_env_file" ]

    run cat "$das_env_file"
    assert_output "configpath=${das_config_file}"
}

@test "config set accepts loopback vault.endpoint hosts" {
    use_config "simple"
    ensure_env

    for endpoint in localhost:40010 localhost:40011 127.0.0.1:40010; do
        run das-cli config set "vault.endpoint=${endpoint}"
        assert_success

        run get_config ".vault.endpoint"
        assert_output "$endpoint"
    done
}

@test "config set rejects a non-loopback vault.endpoint hostname" {
    use_config "simple"
    ensure_env

    run das-cli config set vault.endpoint=vault.example:40010
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"

    run das-cli config set vault.endpoint=0.0.0.0:40010
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"
}

@test "config set rejects a non-numeric vault.endpoint port" {
    use_config "simple"
    ensure_env

    run das-cli config set vault.endpoint=localhost:abc
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"
}

@test "config set rejects out-of-range vault.endpoint ports" {
    use_config "simple"
    ensure_env

    for endpoint in localhost:0 localhost:65536; do
        run das-cli config set "vault.endpoint=${endpoint}"
        assert_failure
        assert_output --partial "vault.endpoint"

        run get_config ".vault.endpoint"
        assert_output "localhost:40010"
    done
}

@test "config set rejects malformed vault.endpoint strings" {
    use_config "simple"
    ensure_env

    for endpoint in :40010 localhost:40010:extra; do
        run das-cli config set "vault.endpoint=${endpoint}"
        assert_failure
        assert_output --partial "vault.endpoint"

        run get_config ".vault.endpoint"
        assert_output "localhost:40010"
    done
}

config_set_answers_before_vault() {
    # save path, decline overwrite, then AtomDB / agents / jupyter defaults
    printf '%s\n' "" "n"
    local i
    for i in $(seq 1 36); do
        printf '\n'
    done
}

run_interactive_config_set() {
    set -o pipefail
    {
        config_set_answers_before_vault
        printf '%s\n' "$1" "$2"
    } | das-cli config set
}

@test "interactive config set keeps the default vault.endpoint" {
    use_config "simple"
    ensure_env

    run run_interactive_config_set "" ""
    assert_success

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"
}

@test "interactive config set persists a custom loopback vault port" {
    use_config "simple"
    ensure_env

    run run_interactive_config_set "localhost" "40011"
    assert_success

    run get_config ".vault.endpoint"
    assert_output "localhost:40011"
}

@test "interactive config set rejects a non-loopback vault hostname" {
    use_config "simple"
    ensure_env

    run run_interactive_config_set "vault.example" "40010"
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"
}

@test "config set --file rejects an invalid vault.endpoint" {
    use_config "simple"
    ensure_env

    local invalid_config
    invalid_config="$(mktemp)"
    cp "${test_fixtures_dir}/config/simple.json" "$invalid_config"
    update_json_key "$invalid_config" vault.endpoint "vault.example:40010"

    run das-cli config set --file "$invalid_config"
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"

    rm -f "$invalid_config"
}