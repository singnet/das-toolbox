#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db restart
    das-cli dbms-adapter das-peer restart

    context_file_path="$test_fixtures_dir/dbms_context.txt"
    postgres_container_name="dbms_peer_postgres"
    postgres_password="postgres"
    postgres_username="postgres"
    postgres_database="integration_db"
    postgres_port="5432"
    postgres_initdb="$test_fixtures_dir/sql/db-adapter.sql"
}

teardown() {
    "$(dirname "${BATS_TEST_DIRNAME}")/../scripts/stop_postgres.sh" \
        -n $postgres_container_name
}

@test "Trying run command with unset configuration file" {
    unset_config

    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db --context $context_file_path

    assert_line --partial "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Missing --client-hostname parameter" {
    run das-cli dbms-adapter dbms-peer run --client-port 5432 --client-username postgres --client-password pass --client-database db --context "$context_file_path"
    assert_line --partial "Error: Missing option '--client-hostname'."
}

@test "Missing --client-port parameter" {
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-username postgres --client-password pass --client-database db --context "$context_file_path"
    assert_line --partial "Error: Missing option '--client-port'."
}

@test "Missing --client-username parameter" {
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-password pass --client-database db --context "$context_file_path"
    assert_line --partial "Error: Missing option '--client-username'."
}

@test "Missing --client-password parameter" {
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-database db --context "$context_file_path"
    assert_line --partial "Error: Missing option '--client-password'."
}

@test "Missing --context parameter" {
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db
    assert_line --partial "Error: Missing option '--context'."
}

@test "Invalid path for --context parameter" {
    local invalid_path="/path/invalid"
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db --context "$invalid_path"
    assert_line --partial "Error: Invalid value for '--context': File '$invalid_path' does not exist."
}

@test "Directory provided instead of file for --context" {
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db --context "$test_fixtures_dir"
    assert_line --partial "Error: Invalid value for '--context': File '$test_fixtures_dir' is a directory."
}

@test "Should run DBMS Peer successfuly" {
    "$(dirname "${BATS_TEST_DIRNAME}")/../scripts/start_postgres.sh" \
        -n $postgres_container_name \
        -p $postgres_password \
        -d $postgres_database \
        -u $postgres_username \
        -P $postgres_port \
        -i $postgres_initdb

    sleep 15s

    run is_container_running $postgres_container_name
    assert_success

    local client_hostname="localhost"
    local client_port="$postgres_port"
    local client_username="$postgres_username"
    local client_password="$postgres_password"
    local client_database="$postgres_database"
    local context="$test_fixtures_dir/dbms_context.txt"

    run das-cli dbms-adapter dbms-peer run \
        --client-hostname $client_hostname \
        --client-port $client_port \
        --client-username $client_username \
        --client-password $client_password \
        --client-database $client_database \
        --context "$context"

    assert_line --partial "The 'public.atoms' has been mapped"
    assert_line --partial "Done."
}
