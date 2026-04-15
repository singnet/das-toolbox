#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    peer_port=$(extract_port "$(get_config ".agents.query.ports_range")")
    link_creation_agent_port=$(extract_port "$(get_config ".agents.link_creation.endpoint")")

    service_name="das-link-creation-agent-40003"

    # 🔥 Garante ambiente limpo
    stop_listen_port "$link_creation_agent_port" 2>/dev/null || true

    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100
    das-cli link-creation-agent stop
}

teardown() {
    das-cli link-creation-agent stop
    stop_listen_port "$link_creation_agent_port" 2>/dev/null || true

    das-cli attention-broker stop
    das-cli query-agent stop
}

@test "Fails to start the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to stop the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent stop

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Fails to restart the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "Start Link Creation Agent when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please start the required services"

    run is_service_up das-query-engine-40002
    assert_failure

    run is_service_up "$service_name"
    assert_failure
}

@test "Start Link Creation Agent when port is already in use" {
    run listen_port "${link_creation_agent_port}"
    assert_success

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "[PortBindingError]"
    assert_output --partial "already in use"
    assert_output --partial "${link_creation_agent_port}"

    run stop_listen_port "${link_creation_agent_port}"
    assert_success

    run is_service_up "$service_name"
    assert_failure
}

@test "Starting the Link Creation Agent when it's already up" {
    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "Starting Link Creation Agent service"
    assert_output --partial "${link_creation_agent_port}"

    run is_service_up "$service_name"
    assert_success
}

@test "Starting the Link Creation Agent" {
    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "Link Creation Agent started listening on the ports"
    assert_output --partial "${link_creation_agent_port}"

    run is_service_up "$service_name"
    assert_success
}

@test "Stopping the Link Creation Agent when it's up-and-running" {
    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    run das-cli link-creation-agent stop

    assert_output --partial "Link Creation Agent service stopped"

    run is_service_up "$service_name"
    assert_failure
}

@test "Stopping the Link Creation Agent when it's already stopped" {
    run das-cli link-creation-agent stop

    assert_output --partial "already stopped"

    run is_service_up "$service_name"
    assert_failure
}

@test "Restarting the Link Creation Agent when it's up-and-running" {
    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "Stopping Link Creation Agent service"
    assert_output --partial "Starting Link Creation Agent service"
    assert_output --partial "${link_creation_agent_port}"

    run is_service_up "$service_name"
    assert_success
}

@test "Restarting the Link Creation Agent when it's not up" {
    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output --partial "already stopped"
    assert_output --partial "Link Creation Agent started listening on the ports"
    assert_output --partial "${link_creation_agent_port}"

    run is_service_up "$service_name"
    assert_success
}