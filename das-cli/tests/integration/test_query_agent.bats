#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

safe_stop() {
    das-cli "$1" stop >/dev/null 2>&1 || true
}

setup() {
    use_config "simple" || true

    query_agent_port="$(extract_port "$(get_config .agents.query.endpoint 2>/dev/null || echo localhost:40002)")"

    stop_listen_port "$query_agent_port" 2>/dev/null || true

    das-cli attention-broker start || true
    das-cli db start || true
    das-cli query-agent stop || true
}

teardown() {
    safe_stop query-agent
    stop_listen_port "$query_agent_port" 2>/dev/null || true

    safe_stop attention-broker
}

@test "Fails to start the Query Agent when configuration file is not set" {
    unset_config

    run das-cli query-agent start --port-range 12000:12100

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to stop the Query Agent when configuration file is not set" {
    unset_config

    run das-cli query-agent stop

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to restart the Query Agent when configuration file is not set" {
    unset_config

    run das-cli query-agent restart --port-range 12000:12100

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Start Query Agent when database is not up" {
    das-cli db stop || true

    run das-cli query-agent start --port-range 12000:12100

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please start the required services"

    run is_service_up das-attention-broker-40001
    assert_success

    run is_service_up das-query-engine-40002
    assert_failure
}

@test "Start Query Agent when attention broker is not up" {
    das-cli attention-broker stop || true

    run das-cli query-agent start --port-range 12000:12100

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please start the required services"

    run is_service_up das-attention-broker-40001
    assert_failure

    run is_service_up das-query-engine-40002
    assert_failure
}

@test "Start Query Agent when port is already in use" {
    run listen_port "${query_agent_port}"
    assert_success

    run das-cli query-agent start --port-range 12000:12100

    assert_failure 1
    assert_output --partial "Starting Query Agent service"
    assert_output --partial "$CONTAINER_START_FAILURE_MESSAGE"

    run stop_listen_port "${query_agent_port}"
    assert_success

    run is_service_up das-query-engine-40002
    assert_failure
}

@test "Starting the Query Agent" {
    run das-cli query-agent start --port-range 12000:12100

    assert_output --partial "Query Agent started on port"
    assert_output --partial "${query_agent_port}"

    run is_service_up das-query-engine-40002
    assert_success
}

@test "Stopping the Query Agent when it's up-and-running" {
    das-cli query-agent start --port-range 12000:12100

    run das-cli query-agent stop

    assert_output --partial "Query Agent service stopped"

    run is_service_up das-query-engine-40002
    assert_failure
}

@test "Stopping the Query Agent when it's already stopped" {
    run das-cli query-agent stop

    assert_output --partial "already stopped"

    run is_service_up das-query-engine-40002
    assert_failure
}

@test "Restarting the Query Agent when it's up-and-running" {
    das-cli query-agent start --port-range 12000:12100

    run das-cli query-agent restart --port-range 12000:12100

    assert_output --partial "Stopping Query Agent service"
    assert_output --partial "Starting Query Agent service"
    assert_output --partial "${query_agent_port}"

    run is_service_up das-query-engine-40002
    assert_success
}

@test "Restarting the Query Agent when it's not up" {
    run das-cli query-agent restart --port-range 12000:12100

    assert_output --partial "already stopped"
    assert_output --partial "Query Agent started on port"
    assert_output --partial "${query_agent_port}"

    run is_service_up das-query-engine-40002
    assert_success
}