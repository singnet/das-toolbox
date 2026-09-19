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

@test "listing config with unset configuration file uses default config" {
    unset_config

    run das-cli config list

    assert_success
    assert_output --partial "Configuration listed successfully."
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

@test "raises error when active configpath points to missing file" {
    use_missing_config_path

    run das-cli config list

    assert_failure
    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "service commands fail when active configpath points to missing file" {
    use_missing_config_path

    run das-cli db start

    assert_failure
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

@test "config set default selection removes configpath and uses resolved default path" {
    use_config "simple"
    ensure_env

    run timeout 20 sh -c 'printf "\n" | das-cli config set'
    assert_success

    if [ -f "$das_env_file" ]; then
        run cat "$das_env_file"
        [[ "$output" != *"configpath="* ]]
    fi

    run das-cli config list
    assert_success
    assert_output --partial "Configuration listed successfully."
}

@test "config set default selection removes only configpath from env" {
    use_config "simple"
    mkdir -p "${das_config_dir}"
    cat <<EOF > "${das_env_file}"
configpath=${das_config_file}
FOO=bar
EOF

    run timeout 20 sh -c 'printf "\n" | das-cli config set'
    assert_success

    run cat "$das_env_file"
    assert_success
    [[ "$output" != *"configpath="* ]]
    [[ "$output" == *"FOO=bar"* ]]
}

@test "config set key=value is blocked when active config is default path" {
    use_config "simple"

    set_env_config_path "/usr/share/das/config.json"

    run das-cli config set vault.endpoint=localhost:40123
    assert_failure
    assert_output --partial "Cannot modify default config file"

    run get_config ".vault.endpoint"
    assert_output "localhost:40010"
}