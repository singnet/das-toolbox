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
    das-cli context-broker stop
}

teardown() {
    das-cli context-broker stop
    das-cli query-agent stop
    das-cli attention-broker stop
    das-cli db stop
}

@test "Fails to start the Context Broker when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli context-broker start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$peer_port"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Context Broker when configuration file is not set" {
    unset_config

    run das-cli context-broker stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Context Broker when configuration file is not set" {
    unset_config

    run das-cli context-broker restart \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port 46000

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Context Broker when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli context-broker start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")"

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'context-broker start'.
Run 'query-agent start' to start the Query Agent.[39m"

    run is_service_up query_agent
    assert_failure

    run is_service_up context_broker
    assert_failure
}

@test "Start Context Broker when port is already in use" {
    local context_broker_port="$(get_config .services.context_broker.port)"

    run listen_port "${context_broker_port}"
    assert_success

    run das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800


    assert_output "Starting Context Broker service...
[31m[PortBindingError] Port ${context_broker_port} on localhost are already in use.[39m"


    run stop_listen_port "${context_broker_port}"
    assert_success

    run is_service_up context_broker
    assert_failure
}

@test "Starting the Context Broker when it's already up" {
    local context_broker_port="$(get_config .services.context_broker.port)"

    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Starting Context Broker service...
Context Broker is already running. It's listening on port ${context_broker_port}"

    run is_service_up context_broker

    assert_success
}

@test "Starting the Context Broker" {
    local context_broker_port="$(get_config .services.context_broker.port)"

    run das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Starting Context Broker service...
Context Broker started on port ${context_broker_port}"

    run is_service_up context_broker
    assert_success
}

@test "Stopping the Context Broker when it's up-and-running" {
    local context_broker_port="$(get_config .services.context_broker.port)"

    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli context-broker stop

    assert_output "Stopping Context Broker service...
Context Broker service stopped"

    run is_service_up context_broker
    assert_failure
}

@test "Stopping the Context Broker when it's already stopped" {
    local context_broker_container_name="$(get_config .services.context_broker.container_name)"

    run das-cli context-broker stop

    assert_output "Stopping Context Broker service...
The Context Broker service named ${context_broker_container_name} is already stopped."

    run is_service_up context_broker
    assert_failure
}

@test "Restarting the Context Broker when it's up-and-running" {
    local context_broker_port="$(get_config .services.context_broker.port)"

    das-cli context-broker start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli context-broker restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Stopping Context Broker service...
Context Broker service stopped
Starting Context Broker service...
Context Broker started on port ${context_broker_port}"

    run is_service_up context_broker
    assert_success
}

@test "Restarting the Context Broker when it's not up" {
    local context_broker_container_name="$(get_config .services.context_broker.container_name)"
    local context_broker_port="$(get_config .services.context_broker.port)"

    run das-cli context-broker restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Stopping Context Broker service...
The Context Broker service named ${context_broker_container_name} is already stopped.
Starting Context Broker service...
Context Broker started on port ${context_broker_port}"

    run is_service_up context_broker
    assert_success
}
