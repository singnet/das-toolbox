#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli attention-broker start
    das-cli db start
    das-cli query-agent stop
}

teardown() {
    das-cli db stop
    das-cli attention-broker stop
}

@test "Fails to start the Query Agent when configuration file is not set" {
    unset_config

    run das-cli query-agent start --port-range 12000:12100

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Query Agent when configuration file is not set" {
    unset_config

    run das-cli query-agent stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Query Agent when configuration file is not set" {
    unset_config

    run das-cli query-agent start --port-range 12000:12100

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Query Agent when database is not up" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    das-cli db stop

    run das-cli query-agent start --port-range 12000:12100
    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'query-agent start'.
Run 'db start' to start the databases and 'attention-broker start' to start the Attention Broker.[39m"

    run is_service_up attention_broker
    assert_success

    run is_service_up mongodb
    assert_failure

    run is_service_up redis
    assert_failure

    run is_service_up query_agent
    assert_failure
}

@test "Start Query Agent when attention broker is not up" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    das-cli attention-broker stop

    run das-cli query-agent start --port-range 12000:12100
    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'query-agent start'.
Run 'db start' to start the databases and 'attention-broker start' to start the Attention Broker.[39m"

    run is_service_up attention_broker
    assert_failure

    run is_service_up mongodb
    assert_success

    run is_service_up redis
    assert_success

    run is_service_up query_agent
    assert_failure
}

@test "Start Query Agent when port is already in use" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    run listen_port "${query_agent_port}"
    assert_success

    run das-cli query-agent start --port-range 12000:12100
    assert_output "Starting Query Agent service...
[31m[DockerError] Failed to start Query Agent. Please ensure that the port ${query_agent_port} is not already in use and that the required services are running.[39m"

    run stop_listen_port "${query_agent_port}"
    assert_success

    run is_service_up query_agent
    assert_failure
}

@test "Starting the Query Agent when it's already up" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    das-cli query-agent start --port-range 12000:12100

    run das-cli query-agent start --port-range 12000:12100

    assert_output "Starting Query Agent service...
Query Agent is already running. It's listening on port ${query_agent_port}"

    run is_service_up query_agent

    assert_success
}

@test "Starting the Query Agent" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    run das-cli query-agent start --port-range 12000:12100

    assert_output "Starting Query Agent service...
Query Agent started on port ${query_agent_port}"
    run is_service_up query_agent

    assert_success
}

@test "Stopping the Query Agent when it's up-and-running" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    das-cli query-agent start --port-range 12000:12100

    run das-cli query-agent stop

    assert_output "Stopping Query Agent service...
Query Agent service stopped"

    run is_service_up query_agent

    assert_failure
}

@test "Stopping the Query Agent when it's already stopped" {
    local query_agent_container_name="$(get_config .services.query_agent.container_name)"

    run das-cli query-agent stop

    assert_output "Stopping Query Agent service...
The Query Agent service named ${query_agent_container_name} is already stopped."

    run is_service_up query_agent

    assert_failure
}

@test "Restarting the Query Agent when it's up-and-running" {
    local query_agent_port="$(get_config .services.query_agent.port)"

    das-cli query-agent start --port-range 12000:12100

    run das-cli query-agent restart --port-range 12000:12100

    assert_output "Stopping Query Agent service...
Query Agent service stopped
Starting Query Agent service...
Query Agent started on port ${query_agent_port}"

    run is_service_up query_agent

    assert_success
}

@test "Restarting the Query Agent when it's not up" {
    local query_agent_container_name="$(get_config .services.query_agent.container_name)"
    local query_agent_port="$(get_config .services.query_agent.port)"

    run das-cli query-agent restart --port-range 12000:12100

    assert_output "Stopping Query Agent service...
The Query Agent service named ${query_agent_container_name} is already stopped.
Starting Query Agent service...
Query Agent started on port ${query_agent_port}"

    run is_service_up query_agent

    assert_success
}
