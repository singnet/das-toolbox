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
    das-cli evolution-broker stop
}

teardown() {
    das-cli evolution-broker stop
    das-cli query-agent stop
    das-cli attention-broker stop
    das-cli db stop
}

@test "Fails to start the Evolution Broker when configuration file is not set" {
    unset_config

    run das-cli evolution-broker start --port-range 12700:12800

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Evolution Broker when configuration file is not set" {
    unset_config

    run das-cli evolution-broker stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Evolution Broker when configuration file is not set" {
    unset_config

    run das-cli evolution-broker restart --port-range 12700:12800

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Evolution Broker when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli evolution-broker start --port-range 12700:12800

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'evolution-broker start'.
Run 'query-agent start' to start the Query Agent.[39m"

    run is_service_up query_agent
    assert_failure

    run is_service_up evolution_broker
    assert_failure
}

@test "Start Evolution Broker when port is already in use" {
    local evolution_broker_port="$(get_config .services.evolution_broker.port)"

    run listen_port "${evolution_broker_port}"
    assert_success

    run das-cli evolution-broker start --port-range 12700:12800

    assert_output "Starting Evolution Broker service...
[31m[DockerError] Port ${evolution_broker_port} is already in use. Please stop the service that is currently using this port.[39m"

    run stop_listen_port "${evolution_broker_port}"
    assert_success

    run is_service_up evolution_broker
    assert_failure
}

@test "Starting the Evolution Broker when it's already up" {
    local evolution_broker_port="$(get_config .services.evolution_broker.port)"

    das-cli evolution-broker start --port-range 12700:12800

    run das-cli evolution-broker start --port-range 12700:12800

    assert_output "Starting Evolution Broker service...
Evolution Broker is already running. It's listening on port ${evolution_broker_port}"

    run is_service_up evolution_broker

    assert_success
}

@test "Starting the Evolution Broker" {
    local evolution_broker_port="$(get_config .services.evolution_broker.port)"

    run das-cli evolution-broker start --port-range 12700:12800

    assert_output "Starting Evolution Broker service...
Evolution Broker started on port ${evolution_broker_port}"

    run is_service_up evolution_broker
    assert_success
}

@test "Stopping the Evolution Broker when it's up-and-running" {
    local evolution_broker_port="$(get_config .services.evolution_broker.port)"

    das-cli evolution-broker start --port-range 12700:12800

    run das-cli evolution-broker stop

    assert_output "Stopping Evolution Broker service...
Evolution Broker service stopped"

    run is_service_up evolution_broker
    assert_failure
}

@test "Stopping the Evolution Broker when it's already stopped" {
    local evolution_broker_container_name="$(get_config .services.evolution_broker.container_name)"

    run das-cli evolution-broker stop

    assert_output "Stopping Evolution Broker service...
The Evolution Broker service named ${evolution_broker_container_name} is already stopped."

    run is_service_up evolution_broker
    assert_failure
}

@test "Restarting the Evolution Broker when it's up-and-running" {
    local evolution_broker_port="$(get_config .services.evolution_broker.port)"

    das-cli evolution-broker start --port-range 12700:12800

    run das-cli evolution-broker restart --port-range 12700:12800

    assert_output "Stopping Evolution Broker service...
Evolution Broker service stopped
Starting Evolution Broker service...
Evolution Broker started on port ${evolution_broker_port}"

    run is_service_up evolution_broker
    assert_success
}

@test "Restarting the Evolution Broker when it's not up" {
    local evolution_broker_container_name="$(get_config .services.evolution_broker.container_name)"
    local evolution_broker_port="$(get_config .services.evolution_broker.port)"

    run das-cli evolution-broker restart --port-range 12700:12800

    assert_output "Stopping Evolution Broker service...
The Evolution Broker service named ${evolution_broker_container_name} is already stopped.
Starting Evolution Broker service...
Evolution Broker started on port ${evolution_broker_port}"

    run is_service_up evolution_broker
    assert_success
}
