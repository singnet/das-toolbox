#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    skip "Tests skipped: dbms commands were temporarily disabled."

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
    skip "Tests skipped: dbms commands were temporarily disabled."

    "$(dirname "${BATS_TEST_DIRNAME}")/../scripts/stop_postgres.sh" \
        -n $postgres_container_name
}

@test "Trying run command with unset configuration file" { 
    unset_config

    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db --configpath $context_file_path

    assert_line --partial "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Invalid path for --configpath parameter" {
    local invalid_path="/path/invalid"
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db --configpath "$invalid_path"
    assert_line --partial "Error: Invalid value for '--configpath': File '$invalid_path' does not exist."
}

@test "Directory provided instead of file for --configpath" {
    run das-cli dbms-adapter dbms-peer run --client-hostname localhost --client-port 5432 --client-username postgres --client-password pass --client-database db --configpath "$test_fixtures_dir"
    assert_line --partial "Error: Invalid value for '--configpath': File '$test_fixtures_dir' is a directory."
}

@test "DBMS Peer should not start when server is not up and running" {
    das-cli dbms-adapter das-peer stop

    run is_service_up das_peer

    assert_failure

    local client_hostname="localhost"
    local client_port="$postgres_port"
    local client_username="$postgres_username"
    local client_password="$postgres_password"
    local client_database="$postgres_database"

    run das-cli dbms-adapter dbms-peer run \
        --client-hostname $client_hostname \
        --client-port $client_port \
        --client-username $client_username \
        --client-password $client_password \
        --client-database $client_database \
        --context "$context_file_path"

    assert_output "[31m[DockerContainerNotFoundError] 
The server is not running. Please start the server by executing \`dbms das-peer start\` before attempting to run this command.[39m"
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

    local client_hostname="$(get_docker_gateway "$postgres_container_name")"
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
        --configpath "$context"\

    assert_line --partial "Starting DBMS Peer $client_hostname:$client_port"
    assert_line --partial "The 'public.atoms' has been mapped"
    assert_line --partial "DBMS Peer client started successfully on $client_hostname:$client_port. It will now connect to the DAS peer server and synchronize data."
}
