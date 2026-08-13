#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'


safe_reset_broker() {
    das-cli atomdb-broker stop >/dev/null 2>&1 || true
    sleep 0.2
}


setup() {
    use_config "simple"
    das-cli db start

    safe_reset_broker
}


teardown() {
    das-cli atomdb-broker stop >/dev/null 2>&1 || true
}

@test "Trying to start, stop and restart atomdb-broker with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli atomdb-broker "$cmd"
        assert_output --partial "$FILE_NOT_FOUND_ERROR"
    done
}


@test "Start atomdb-broker when port is already in use" {
    use_config "simple"

    local atomdb_broker_endpoint="$(get_config .agents.atomdb.endpoint)"
    local atomdb_broker_port="$(extract_port "$atomdb_broker_endpoint")"

    run listen_port "${atomdb_broker_port}"
    assert_success

    safe_reset_broker

    run das-cli atomdb-broker start

    assert_failure 1
    assert_output --partial "Starting AtomDB Broker service..."
    assert_output --partial "$CONTAINER_START_FAILURE_MESSAGE"

    run stop_listen_port "${atomdb_broker_port}"
    assert_success

    run is_service_up das-atomdb-broker-40007
    assert_failure
}


@test "Starting atomdb-broker when it's already up" {
    use_config "simple"

    local atomdb_broker_endpoint="$(get_config .agents.atomdb.endpoint)"
    local atomdb_broker_port="$(extract_port "$atomdb_broker_endpoint")"

    safe_reset_broker

    das-cli atomdb-broker start

    run das-cli atomdb-broker start

    assert_output "Starting AtomDB Broker service...
AtomDB Broker is already running. It's listening on port ${atomdb_broker_port}"
}


@test "Starting the atomdb-broker" {
    use_config "simple"

    local atomdb_broker_endpoint="$(get_config .agents.atomdb.endpoint)"
    local atomdb_broker_port="$(extract_port "$atomdb_broker_endpoint")"

    safe_reset_broker

    run das-cli atomdb-broker start

    assert_output "Starting AtomDB Broker service...
AtomDB Broker started on port ${atomdb_broker_port}"

    run is_service_up das-atomdb-broker-40007
    assert_success
}


@test "Stopping atomdb-broker when it's up-and-running" {
    use_config "simple"

    local atomdb_broker_endpoint="$(get_config .agents.atomdb.endpoint)"
    local atomdb_broker_port="$(extract_port "$atomdb_broker_endpoint")"

    safe_reset_broker
    das-cli atomdb-broker start

    run das-cli atomdb-broker stop

    assert_output "Stopping AtomDB Broker service...
AtomDB Broker service stopped"
}


@test "Stopping atomdb-broker when it's already stopped" {
    use_config "simple"

    run das-cli atomdb-broker stop

    assert_output "Stopping AtomDB Broker service...
The AtomDB Broker service named das-atomdb-broker-40007 is already stopped."

    run is_service_up das-atomdb-broker-40007
    assert_failure
}


@test "Restarting atomdb-broker when it's up-and-running" {
    use_config "simple"

    local atomdb_broker_endpoint="$(get_config .agents.atomdb.endpoint)"
    local atomdb_broker_port="$(extract_port "$atomdb_broker_endpoint")"

    safe_reset_broker
    das-cli atomdb-broker start

    run das-cli atomdb-broker restart

    assert_output "Stopping AtomDB Broker service...
AtomDB Broker service stopped
Starting AtomDB Broker service...
AtomDB Broker started on port ${atomdb_broker_port}"

    run is_service_up das-atomdb-broker-40007
    assert_success
}


@test "Restarting atomdb-broker when it's not up" {
    use_config "simple"

    local atomdb_broker_endpoint="$(get_config .agents.atomdb.endpoint)"
    local atomdb_broker_port="$(extract_port "$atomdb_broker_endpoint")"

    safe_reset_broker

    run das-cli atomdb-broker restart

    assert_output --partial "Stopping AtomDB Broker service...
The AtomDB Broker service named das-atomdb-broker-40007 is already stopped.
Starting AtomDB Broker service...
AtomDB Broker started on port ${atomdb_broker_port}"

    run is_service_up das-atomdb-broker-40007
    assert_success
}
