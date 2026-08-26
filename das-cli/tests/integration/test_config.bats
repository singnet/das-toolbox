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
    assert_output "localhost:8200"

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

    for endpoint in localhost:8200 localhost:8210 127.0.0.1:8200 0.0.0.0:8200; do
        run das-cli config set "vault.endpoint=${endpoint}"
        assert_success

        run get_config ".vault.endpoint"
        assert_output "$endpoint"
    done
}

@test "config set rejects a non-loopback vault.endpoint hostname" {
    use_config "simple"
    ensure_env

    run das-cli config set vault.endpoint=vault.example:8200
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:8200"
}

@test "config set rejects a non-numeric vault.endpoint port" {
    use_config "simple"
    ensure_env

    run das-cli config set vault.endpoint=localhost:abc
    assert_failure
    assert_output --partial "vault.endpoint"

    run get_config ".vault.endpoint"
    assert_output "localhost:8200"
}

@test "config set rejects out-of-range vault.endpoint ports" {
    use_config "simple"
    ensure_env

    for endpoint in localhost:0 localhost:65536; do
        run das-cli config set "vault.endpoint=${endpoint}"
        assert_failure
        assert_output --partial "vault.endpoint"

        run get_config ".vault.endpoint"
        assert_output "localhost:8200"
    done
}

@test "config set rejects malformed vault.endpoint strings" {
    use_config "simple"
    ensure_env

    for endpoint in :8200 localhost:8200:extra; do
        run das-cli config set "vault.endpoint=${endpoint}"
        assert_failure
        assert_output --partial "vault.endpoint"

        run get_config ".vault.endpoint"
        assert_output "localhost:8200"
    done
}