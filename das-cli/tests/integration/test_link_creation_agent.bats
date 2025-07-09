#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start
    das-cli link-creation-agent stop

    reserved_port_range="$(get_port_range --range=1000)"
}

teardown() {
    das-cli attention-broker stop
    das-cli query-agent stop
    das-cli db stop

    release_port_range --range="$reserved_port_range"
}

@test "Fails to start the Link Creation Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range "$reserved_port_range"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Link Creation Agent when configuration file is not set" {
    unset_config

    run das-cli link-creation-agent stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Link Creation Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range "$reserved_port_range"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Link Creation Agent when Query Agent is not up" {
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    das-cli query-agent stop

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'link-creation-agent start'.
Run 'query-agent start' to start the Query Agent.[39m"

    run is_service_up query_agent
    assert_failure

    run is_service_up link_creation_agent
    assert_failure
}

@test "Start Link Creation Agent when port is already in use" {
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    run listen_port "${link_creation_agent_port}"
    assert_success

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    assert_output "Starting Link Creation Agent service...
[31m[DockerError] Port ${link_creation_agent_port} is already in use. Please stop the service that is currently using this port.[39m"

    run stop_listen_port "${link_creation_agent_port}"
    assert_success

    run is_service_up link_creation_agent
    assert_failure
}

@test "Starting the Link Creation Agent when it's already up" {
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    assert_output "Starting Link Creation Agent service...
Link Creation Agent is already running. It's listening on the ports ${link_creation_agent_port}"

    run is_service_up link_creation_agent

    assert_success
}

@test "Starting the Link Creation Agent" {
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    run das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    assert_output "Starting Link Creation Agent service...
Link Creation Agent started listening on the ports ${link_creation_agent_port}"

    run is_service_up link_creation_agent
    assert_success
}

@test "Stopping the Link Creation Agent when it's up-and-running" {
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    run das-cli link-creation-agent stop

    assert_output "Stopping Link Creation Agent service...
Link Creation Agent service stopped"

    run is_service_up link_creation_agent
    assert_failure
}

@test "Stopping the Link Creation Agent when it's already stopped" {
    local link_creation_agent_container_name="$(get_config .services.link_creation_agent.container_name)"

    run das-cli link-creation-agent stop

    assert_output "Stopping Link Creation Agent service...
The Link Creation Agent service named ${link_creation_agent_container_name} is already stopped."

    run is_service_up link_creation_agent
    assert_failure
}

@test "Restarting the Link Creation Agent when it's up-and-running" {
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    assert_output "Stopping Link Creation Agent service...
Link Creation Agent service stopped
Starting Link Creation Agent service...
Link Creation Agent started listening on the ports ${link_creation_agent_port}"

    run is_service_up link_creation_agent
    assert_success
}

@test "Restarting the Link Creation Agent when it's not up" {
    local link_creation_agent_container_name="$(get_config .services.link_creation_agent.container_name)"
    local link_creation_agent_port="$(get_config .services.link_creation_agent.port)"

    run das-cli link-creation-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range "$reserved_port_range"

    assert_output "Stopping Link Creation Agent service...
The Link Creation Agent service named ${link_creation_agent_container_name} is already stopped.
Starting Link Creation Agent service...
Link Creation Agent started listening on the ports ${link_creation_agent_port}"

    run is_service_up link_creation_agent
    assert_success
}
