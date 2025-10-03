#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db start
    das-cli attention-broker start
    das-cli query-agent start --port-range 12000:12100
    das-cli context-agent stop
}

teardown() {
    das-cli context-agent stop
    das-cli query-agent stop
    das-cli attention-broker stop
    das-cli db stop
}

@test "Fails to start the Context Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli context-agent start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$peer_port"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Context Agent when configuration file is not set" {
    unset_config

    run das-cli context-agent stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Context Agent when configuration file is not set" {
    unset_config

    run das-cli context-agent restart \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port 46000

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Context Agent when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli context-agent start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")"

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'context-agent start'.
Run 'query-agent start' to start the Query Agent.[39m"

    run is_service_up query_agent
    assert_failure

    run is_service_up context_agent
    assert_failure
}

@test "Start Context Agent when port is already in use" {
    local context_agent_port="$(get_config .services.context_agent.port)"

    run listen_port "${context_agent_port}"
    assert_success

    run das-cli context-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800


    assert_output "Starting Context Agent service...
[31m[PortBindingError] Port ${context_agent_port} on localhost are already in use.[39m"


    run stop_listen_port "${context_agent_port}"
    assert_success

    run is_service_up context_agent
    assert_failure
}

@test "Starting the Context Agent when it's already up" {
    local context_agent_port="$(get_config .services.context_agent.port)"

    das-cli context-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli context-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Starting Context Agent service...
Context Agent is already running. It's listening on port ${context_agent_port}"

    run is_service_up context_agent

    assert_success
}

@test "Starting the Context Agent" {
    local context_agent_port="$(get_config .services.context_agent.port)"

    run das-cli context-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Starting Context Agent service...
Context Agent started on port ${context_agent_port}"

    run is_service_up context_agent
    assert_success
}

@test "Stopping the Context Agent when it's up-and-running" {
    local context_agent_port="$(get_config .services.context_agent.port)"

    das-cli context-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli context-agent stop

    assert_output "Stopping Context Agent service...
Context Agent service stopped"

    run is_service_up context_agent
    assert_failure
}

@test "Stopping the Context Agent when it's already stopped" {
    local context_agent_container_name="$(get_config .services.context_agent.container_name)"

    run das-cli context-agent stop

    assert_output "Stopping Context Agent service...
The Context Agent service named ${context_agent_container_name} is already stopped."

    run is_service_up context_agent
    assert_failure
}

@test "Restarting the Context Agent when it's up-and-running" {
    local context_agent_port="$(get_config .services.context_agent.port)"

    das-cli context-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli context-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Stopping Context Agent service...
Context Agent service stopped
Starting Context Agent service...
Context Agent started on port ${context_agent_port}"

    run is_service_up context_agent
    assert_success
}

@test "Restarting the Context Agent when it's not up" {
    local context_agent_container_name="$(get_config .services.context_agent.container_name)"
    local context_agent_port="$(get_config .services.context_agent.port)"

    run das-cli context-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Stopping Context Agent service...
The Context Agent service named ${context_agent_container_name} is already stopped.
Starting Context Agent service...
Context Agent started on port ${context_agent_port}"

    run is_service_up context_agent
    assert_success
}
