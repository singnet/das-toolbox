#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

safe_stop_adapter() {
    das-cli database-adapter stop >/dev/null 2>&1 || true
    sleep 0.2
}

setup() {
    use_config "simple"

    das-cli db start

    safe_stop_adapter
}

teardown() {
    safe_stop_adapter
}

@test "Trying to run database-adapter with unset configuration file" {
    unset_config

    run das-cli database-adapter run

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Starting database-adapter" {
    use_config "simple"

    safe_stop_adapter

    run das-cli database-adapter run

    assert_output "Starting Database Adapter...
Database Adapter started successfully."
}

@test "Stopping database-adapter" {
    use_config "simple"

    safe_stop_adapter

    das-cli database-adapter run

    run das-cli database-adapter stop

    assert_output "Stopping Database Adapter...
Database Adapter stopped successfully."
}

@test "Stopping database-adapter when already stopped" {
    use_config "simple"

    safe_stop_adapter

    run das-cli database-adapter stop

    assert_output --partial "already stopped"
}