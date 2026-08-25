#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    vault_port="$(extract_port "$(get_config .vault.endpoint)")"
    vault_container="das-cli-vault-8200"

    das-cli vault stop &>/dev/null || true
    stop_listen_port "$vault_port" &>/dev/null || true
}

teardown() {
    das-cli vault stop &>/dev/null || true
}

@test "Trying to start and stop Vault with unset configuration file" {
    local cmds=(start stop)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli vault "$cmd"
        assert_output --partial "$FILE_NOT_FOUND_ERROR"
    done
}

@test "Starting Vault" {
    run das-cli vault start

    assert_success
    assert_output --partial "Starting Vault"
    assert_output --partial "started on port"
    assert_output --partial "$vault_port"
    assert_output --partial "http://localhost:${vault_port}/ui"
    assert_output --partial "admin password:"

    run is_service_up "$vault_container"
    assert_success

    run docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$vault_container"
    refute_output --partial "BAO_DEV_ROOT_TOKEN_ID="
    refute_output --partial "BAO_DEV_LISTEN_ADDRESS="
}

@test "Trying to start Vault after it has been started" {
    run das-cli vault start
    assert_success

    run das-cli vault start

    assert_output --partial "already running"
    assert_output --partial "$vault_port"

    run is_service_up "$vault_container"
    assert_success
}

@test "Stopping Vault" {
    das-cli vault start

    run das-cli vault stop

    assert_output --partial "service stopped"

    run is_service_up "$vault_container"
    assert_failure
}

@test "Trying to stop Vault after already stopped" {
    run das-cli vault stop

    assert_output --partial "already stopped"

    run is_service_up "$vault_container"
    assert_failure
}
