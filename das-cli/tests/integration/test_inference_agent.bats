#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    das-cli attention-broker start
    das-cli db start

    # limpa estado anterior
    das-cli inference-agent stop &>/dev/null || true

    inference_agent_port="$(extract_port "$(get_config .agents.inference.endpoint)")"
    query_agent_port="$(extract_port "$(get_config .agents.query.endpoint)")"

    # garante porta livre (CRÍTICO)
    stop_listen_port "$inference_agent_port" &>/dev/null || true

    service_name="das-inference-agent-40004"
}

teardown() {
    das-cli inference-agent stop &>/dev/null || true
    das-cli attention-broker stop &>/dev/null || true
}

@test "Fails to start the Inference Agent when configuration file is not set" {
    unset_config

    run das-cli inference-agent start \
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to stop the Inference Agent when configuration file is not set" {
    unset_config

    run das-cli inference-agent stop

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to restart the Inference Agent when configuration file is not set" {
    unset_config

    run das-cli inference-agent restart \
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Start Inference Agent when Attention Broker is not up" {
    das-cli attention-broker stop

    run das-cli inference-agent start \
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please start the required services"

    run is_service_up das-attention-broker-40001
    assert_failure

    run is_service_up "$service_name"
    assert_failure
}

@test "Start Inference Agent when port is already in use" {
    run listen_port "$inference_agent_port"
    assert_success

    run das-cli inference-agent start \
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    # ⚠️ NÃO use variável genérica aqui
    assert_output --partial "[PortBindingError]"
    assert_output --partial "already in use"

    run stop_listen_port "$inference_agent_port"
    assert_success

    run is_service_up "$service_name"
    assert_failure
}

@test "Starting the Inference Agent when it's already up" {
    # garante que subiu
    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600
    assert_success

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output --partial "already running"

    run is_service_up "$service_name"
    assert_success
}

@test "Starting the Inference Agent" {
    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_success
    assert_output --partial "started listening on the ports"
    assert_output --partial "$inference_agent_port"

    run is_service_up "$service_name"
    assert_success
}

@test "Stopping the Inference Agent when it's up-and-running" {
    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    run das-cli inference-agent stop

    assert_output --partial "service stopped"

    run is_service_up "$service_name"
    assert_failure
}

@test "Stopping the Inference Agent when it's already stopped" {
    run das-cli inference-agent stop

    assert_output --partial "already stopped"

    run is_service_up "$service_name"
    assert_failure
}

@test "Restarting the Inference Agent when it's up-and-running" {
    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output --partial "Stopping Inference Agent service"
    assert_output --partial "Starting Inference Agent service"
    assert_output --partial "$inference_agent_port"

    run is_service_up "$service_name"
    assert_success
}

@test "Restarting the Inference Agent when it's not up" {
    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output --partial "already stopped"
    assert_output --partial "started listening on the ports"
    assert_output --partial "$inference_agent_port"

    run is_service_up "$service_name"
    assert_success
}