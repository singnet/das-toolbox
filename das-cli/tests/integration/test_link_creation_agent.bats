#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    # Query agent peer port
    local peer_endpoint
    peer_endpoint=$(get_config ".agents.query.ports_range")
    peer_port=$(extract_port "$peer_endpoint")

    # Link creation agent port
    local link_endpoint
    link_endpoint=$(get_config ".agents.link_creation.endpoint")
    link_creation_agent_port=$(extract_port "$link_endpoint")

    service_name="das-link-creation-agent-40003"

    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100
    das-cli link-creation-agent stop
}

teardown() {
    das-cli attention-broker stop
    das-cli query-agent stop
}

@test "Fails to start the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Link Creation Agent when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'link-creation-agent start'.
Run 'query-agent start' to start the Query Agent.[39m"

    run is_service_up das-query-engine-40002
    assert_failure

    run is_service_up $service_name
    assert_failure
}

@test "Start Link Creation Agent when port is already in use" {
    run listen_port "${link_creation_agent_port}"
    assert_success

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output "Starting Link Creation Agent service...
[31m[PortBindingError] Port ${link_creation_agent_port} on localhost are already in use.[39m"

    run stop_listen_port "${link_creation_agent_port}"
    assert_success

    run is_service_up $service_name
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

    assert_output "Starting Link Creation Agent service...
Link Creation Agent is already running. It's listening on the ports ${link_creation_agent_port}"

    run is_service_up $service_name
    assert_success
}

@test "Starting the Link Creation Agent" {
    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output "Starting Link Creation Agent service...
Link Creation Agent started listening on the ports ${link_creation_agent_port}"

    run is_service_up $service_name
    assert_success
}

@test "Stopping the Link Creation Agent when it's up-and-running" {
    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    run das-cli link-creation-agent stop

    assert_output "Stopping Link Creation Agent service...
Link Creation Agent service stopped"

    run is_service_up $service_name
    assert_failure
}

@test "Stopping the Link Creation Agent when it's already stopped" {
    run das-cli link-creation-agent stop

    assert_output "Stopping Link Creation Agent service...
The Link Creation Agent service named ${service_name} is already stopped."

    run is_service_up $service_name
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

    assert_output "Stopping Link Creation Agent service...
Link Creation Agent service stopped
Starting Link Creation Agent service...
Link Creation Agent started listening on the ports ${link_creation_agent_port}"

    run is_service_up $service_name
    assert_success
}

@test "Restarting the Link Creation Agent when it's not up" {
    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12300:12400

    assert_output "Stopping Link Creation Agent service...
The Link Creation Agent service named ${service_name} is already stopped.
Starting Link Creation Agent service...
Link Creation Agent started listening on the ports ${link_creation_agent_port}"

    run is_service_up $service_name
    assert_success
}