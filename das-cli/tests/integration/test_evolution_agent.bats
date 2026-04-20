#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    das-cli db start
    das-cli attention-broker start
    das-cli query-agent start --port-range 12000:12100

    # limpeza forte de estado
    das-cli evolution-agent stop &>/dev/null || true

    local evolution_agent_port
    evolution_agent_port="$(extract_port "$(get_config .agents.evolution.endpoint)")"
    stop_listen_port "$evolution_agent_port" &>/dev/null || true
}

teardown() {
    das-cli evolution-agent stop &>/dev/null || true
    das-cli query-agent stop &>/dev/null || true
    das-cli attention-broker stop &>/dev/null || true
}

@test "Fails to start the Evolution Agent when configuration file is not set" {
    unset_config

    run das-cli evolution-agent start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port 12000

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to stop the Evolution Agent when configuration file is not set" {
    unset_config

    run das-cli evolution-agent stop

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to restart the Evolution Agent when configuration file is not set" {
    unset_config

    run das-cli evolution-agent restart \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port 42000

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Start Evolution Agent when Query Agent is not up" {
    das-cli query-agent stop

    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    run das-cli evolution-agent start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$query_agent_port"

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please start the required services"

    run is_service_up query_agent
    assert_failure

    run is_service_up das-evolution-agent-40005
    assert_failure
}

@test "Start Evolution Agent when port is already in use" {
    local evolution_agent_port
    evolution_agent_port="$(extract_port "$(get_config .agents.evolution.endpoint)")"

    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    run listen_port "$evolution_agent_port"
    assert_success

    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    assert_output --partial "[PortBindingError]"
    assert_output --partial "already in use"

    run stop_listen_port "$evolution_agent_port"
    assert_success

    run is_service_up das-evolution-agent-40005
    assert_failure
}

@test "Starting the Evolution Agent when it's already up" {
    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    # garante que subiu
    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800
    assert_success

    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    assert_output --partial "already running"

    run is_service_up das-evolution-agent-40005
    assert_success
}

@test "Starting the Evolution Agent" {
    local evolution_agent_port
    evolution_agent_port="$(extract_port "$(get_config .agents.evolution.endpoint)")"

    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    assert_success
    assert_output --partial "started on port"
    assert_output --partial "$evolution_agent_port"

    run is_service_up das-evolution-agent-40005
    assert_success
}

@test "Stopping the Evolution Agent when it's up-and-running" {
    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    run das-cli evolution-agent stop

    assert_output --partial "service stopped"

    run is_service_up das-evolution-agent-40005
    assert_failure
}

@test "Stopping the Evolution Agent when it's already stopped" {
    run das-cli evolution-agent stop

    assert_output --partial "already stopped"

    run is_service_up das-evolution-agent-40005
    assert_failure
}

@test "Restarting the Evolution Agent when it's up-and-running" {
    local evolution_agent_port
    evolution_agent_port="$(extract_port "$(get_config .agents.evolution.endpoint)")"

    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    run das-cli evolution-agent restart \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    assert_output --partial "Stopping Evolution Agent service"
    assert_output --partial "Starting Evolution Agent service"
    assert_output --partial "$evolution_agent_port"

    run is_service_up das-evolution-agent-40005
    assert_success
}

@test "Restarting the Evolution Agent when it's not up" {
    local evolution_agent_port
    evolution_agent_port="$(extract_port "$(get_config .agents.evolution.endpoint)")"

    local query_agent_port
    query_agent_port="$(extract_port "$(get_config ".agents.query.endpoint")")"

    run das-cli evolution-agent restart \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12700:12800

    assert_output --partial "already stopped"
    assert_output --partial "started on port"
    assert_output --partial "$evolution_agent_port"

    run is_service_up das-evolution-agent-40005
    assert_success
}