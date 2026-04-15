#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    local peer_endpoint
    peer_endpoint=$(get_config ".agents.query.ports_range")
    peer_port=$(extract_port "$peer_endpoint")

    local context_endpoint
    context_endpoint=$(get_config ".brokers.context.endpoint")
    context_broker_port=$(extract_port "$context_endpoint")

    service_name="das-context-broker-${context_broker_port}"

    das-cli db start
    das-cli attention-broker start
    das-cli query-agent start --port-range 12000:12100
    das-cli context-broker stop
}

teardown() {
    das-cli query-agent stop
    das-cli attention-broker stop
    das-cli context-broker stop
}

@test "Fails to start the Context Broker when configuration file is not set" {
    unset_config

    run das-cli context-broker start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$peer_port"

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to stop the Context Broker when configuration file is not set" {
    unset_config

    run das-cli context-broker stop

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to restart the Context Broker when configuration file is not set" {
    unset_config

    run das-cli context-broker restart \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$peer_port"

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Start Context Broker when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli context-broker start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$peer_port"

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please start the required services"

    run is_service_up das-query-engine-40002
    assert_failure

    run is_service_up "$service_name"
    assert_failure
}

@test "Start Context Broker when port is already in use" {
    run listen_port "${context_broker_port}"
    assert_success

    run das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    assert_output --partial "$PORT_IN_USE_ERROR"

    run stop_listen_port "${context_broker_port}"
    assert_success

    run is_service_up "$service_name"
    assert_failure
}

@test "Starting the Context Broker when it's already up" {
    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    run das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    assert_output --partial "Starting Context Broker service"
    assert_output --partial "already running"

    run is_service_up "$service_name"
    assert_success
}

@test "Starting the Context Broker" {
    run das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    assert_output --partial "Context Broker started on port"

    run is_service_up "$service_name"
    assert_success
}

@test "Stopping the Context Broker when it's up-and-running" {
    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    run das-cli context-broker stop

    assert_output --partial "Context Broker service stopped"

    run is_service_up "$service_name"
    assert_failure
}

@test "Stopping the Context Broker when it's already stopped" {
    run das-cli context-broker stop

    assert_output --partial "already stopped"

    run is_service_up "$service_name"
    assert_failure
}

@test "Restarting the Context Broker when it's up-and-running" {
    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    run das-cli context-broker restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    assert_output --partial "Stopping Context Broker service"
    assert_output --partial "Starting Context Broker service"

    run is_service_up "$service_name"
    assert_success
}

@test "Restarting the Context Broker when it's not up" {
    run das-cli context-broker restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12700:12800

    assert_output --partial "already stopped"
    assert_output --partial "Context Broker started on port"

    run is_service_up "$service_name"
    assert_success
}