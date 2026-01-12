#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db start
    das-cli atomdb-broker stop
}

@test "Trying to start, stop and restart atomdb-broker with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli atomdb-broker $cmd

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Start atomdb-broker when port is already in use" {
    use_config "simple"

    local atomdb_broker_port="$(get_config .services.atomdb_broker.port)"

    run listen_port "${atomdb_broker_port}"
    assert_success

    run das-cli atomdb-broker start
    assert_output "Starting AtomDB Broker service...
[31m[PortBindingError] Port ${atomdb_broker_port} on localhost are already in use.[39m"

    run stop_listen_port "${atomdb_broker_port}"
    assert_success

    run is_service_up atomdb_broker
    assert_failure

    run stop_listen_port "${atomdb_broker_port}"
}

@test "Starting atomdb-broker when it's already up" {
    local atomdb_broker_port="$(get_config .services.atomdb_broker.port)"

    das-cli atomdb-broker start

    run das-cli atomdb-broker start

    assert_output "Starting AtomDB Broker service...
AtomDB Broker is already running. It's listening on port ${atomdb_broker_port}"

    run is_service_up atomdb_broker
    assert_success
}

@test "Starting the atomdb-broker" {
    local atomdb_broker_port="$(get_config .services.atomdb_broker.port)"

    run das-cli atomdb-broker start

    assert_output "Starting AtomDB Broker service...
AtomDB Broker started on port ${atomdb_broker_port}"

    run is_service_up atomdb_broker
    assert_success
}

@test "Stopping atomdb-broker when it's up-and-running" {
    local atomdb_broker_port="$(get_config .services.atomdb_broker.port)"

    das-cli atomdb-broker start

    run das-cli atomdb-broker stop

    assert_output "Stopping AtomDB Broker service...
AtomDB Broker service stopped"
}

@test "Stopping atomdb-broker when it's already stopped" {
    local atomdb_broker_container_name="$(get_config .services.atomdb_broker.container_name)"

    run das-cli atomdb-broker stop

    assert_output "Stopping AtomDB Broker service...
The AtomDB Broker service named ${atomdb_broker_container_name} is already stopped."

    run is_service_up atomdb_broker
    assert_failure
}

@test "Restarting atomdb-broker when it's up-and-running" {
    local atomdb_broker_port="$(get_config .services.atomdb_broker.port)"

    das-cli atomdb-broker start

    run das-cli atomdb-broker restart

    assert_output "Stopping AtomDB Broker service...
AtomDB Broker service stopped
Starting AtomDB Broker service...
AtomDB Broker started on port ${atomdb_broker_port}"

    run is_service_up atomdb_broker
    assert_success
}

@test "Restarting atomdb-broker when it's not up" {
    local atomdb_broker_container_name="$(get_config .services.atomdb_broker.container_name)"
    local atomdb_broker_port="$(get_config .services.atomdb_broker.port)"

    run das-cli atomdb-broker restart

    assert_output "Stopping AtomDB Broker service...
The AtomDB Broker service named ${atomdb_broker_container_name} is already stopped.
Starting AtomDB Broker service...
AtomDB Broker started on port ${atomdb_broker_port}"

    run is_service_up atomdb_broker
    assert_success
}
