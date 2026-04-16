#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    peer_port=$(extract_port "$(get_config ".agents.query.ports_range")")

    das-cli db stop
    das-cli attention-broker stop
    das-cli query-agent stop
    das-cli link-creation-agent stop
    das-cli inference-agent stop
    das-cli evolution-agent stop
}

teardown() {
    das-cli attention-broker stop
    das-cli query-agent stop
    das-cli link-creation-agent stop
    das-cli inference-agent stop
    das-cli evolution-agent stop
    das-cli context-broker stop
}

@test "Show logs for MongoDB and Redis with unset configuration file" {
    local services=(mongodb redis)

    unset_config

    for service in "${services[@]}"; do
        run das-cli logs "$service"
        assert_output --partial "$FILE_NOT_FOUND_ERROR"
    done
}

@test "Trying to show logs for MongoDB before db is running" {
    run das-cli logs mongodb -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "MongoDB is not running"

    run is_service_up mongodb
    assert_failure
}

@test "Trying to show logs for Redis before db is running" {
    run das-cli logs redis -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Redis is not running"

    run is_service_up redis
    assert_failure
}

@test "Show logs for Redis and MongoDB" {
    local services=(mongodb redis)

    das-cli db start

    for service in "${services[@]}"; do
        run timeout 5s das-cli logs "${service}" -f
        assert_failure 124
    done
}

@test "Trying to show logs for attention broker before it is running" {
    run das-cli logs attention-broker -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Attention broker is not running"

    run is_service_up attention-broker
    assert_failure
}

@test "Show logs for attention broker" {
    das-cli attention-broker start
    run timeout 5s das-cli logs attention-broker -f

    assert_failure 124
}

@test "Trying to show logs for query agent before it is running" {
    run das-cli logs query-agent -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Query agent is not running"

    run is_service_up query-agent
    assert_failure
}

@test "Show logs for query agent" {
    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100

    run timeout 5s das-cli logs query-agent -f
    assert_failure 124
}

@test "Trying to show logs for link creation agent before it is running" {
    run das-cli logs link-creation-agent -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Link creation agent is not running"

    run is_service_up link-creation-agent
    assert_failure
}

@test "Show logs for link creation agent" {
    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100

    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    run timeout 5s das-cli logs link-creation-agent -f
    assert_failure 124
}

@test "Trying to show logs for inference agent before it is running" {
    run das-cli logs inference-agent -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Inference agent is not running"

    run is_service_up inference-agent
    assert_failure
}

@test "Show logs for inference agent" {
    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100

    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12500:12600

    run timeout 5s das-cli logs inference-agent -f
    assert_failure 124
}

@test "Trying to show logs for evolution agent before it is running" {
    run das-cli logs evolution-agent -f

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Evolution Agent is not running"

    run is_service_up evolution-agent
    assert_failure
}

@test "Show logs for evolution agent" {
    das-cli db start
    das-cli attention-broker start
    das-cli query-agent start --port-range 12000:12100

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    run timeout 5s das-cli logs evolution-agent -f
    assert_failure 124
}

@test "Show logs for context broker" {
    das-cli db start
    das-cli attention-broker start
    das-cli query-agent start --port-range 12000:12100

    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 46000:46999

    run timeout 5s das-cli logs context-broker -f
    assert_failure 124
}

@test "Show DAS logs when the log file does not exist" {
    unset_log

    run timeout 5s das-cli logs das -f

    assert_output --partial "No logs to show"
}

@test "Show logs for DAS" {
    set_log

    run timeout 5s das-cli logs das -f

    assert_output --partial "$(cat "$das_log_file")"
}