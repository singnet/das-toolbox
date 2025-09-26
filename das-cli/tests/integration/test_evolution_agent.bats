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
    das-cli evolution-agent stop
}

teardown() {
    das-cli evolution-agent stop
    das-cli query-agent stop
    das-cli attention-broker stop
    das-cli db stop
}

@test "Fails to start the Evolution Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli evolution-agent start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$peer_port"

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Evolution Agent when configuration file is not set" {
    unset_config

    run das-cli evolution-agent stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Evolution Agent when configuration file is not set" {
    unset_config

    run das-cli evolution-agent restart \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port 42000

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Evolution Agent when Query Agent is not up" {
    das-cli query-agent stop

    run das-cli evolution-agent start \
        --port-range 12700:12800 \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")"

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'evolution-agent start'.
Run 'query-agent start' to start the Query Agent.[39m"

    run is_service_up query_agent
    assert_failure

    run is_service_up evolution_agent
    assert_failure
}

@test "Start Evolution Agent when port is already in use" {
    local evolution_agent_port="$(get_config .services.evolution_agent.port)"

    run listen_port "${evolution_agent_port}"
    assert_success

    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800


    assert_output "Starting Evolution Agent service...
[31m[PortBindingError] Port ${evolution_agent_port} on localhost are already in use.[39m"


    run stop_listen_port "${evolution_agent_port}"
    assert_success

    run is_service_up evolution_agent
    assert_failure
}

@test "Starting the Evolution Agent when it's already up" {
    local evolution_agent_port="$(get_config .services.evolution_agent.port)"

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Starting Evolution Agent service...
Evolution Agent is already running. It's listening on port ${evolution_agent_port}"

    run is_service_up evolution_agent

    assert_success
}

@test "Starting the Evolution Agent" {
    local evolution_agent_port="$(get_config .services.evolution_agent.port)"

    run das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Starting Evolution Agent service...
Evolution Agent started on port ${evolution_agent_port}"

    run is_service_up evolution_agent
    assert_success
}

@test "Stopping the Evolution Agent when it's up-and-running" {
    local evolution_agent_port="$(get_config .services.evolution_agent.port)"

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli evolution-agent stop

    assert_output "Stopping Evolution Agent service...
Evolution Agent service stopped"

    run is_service_up evolution_agent
    assert_failure
}

@test "Stopping the Evolution Agent when it's already stopped" {
    local evolution_agent_container_name="$(get_config .services.evolution_agent.container_name)"

    run das-cli evolution-agent stop

    assert_output "Stopping Evolution Agent service...
The Evolution Agent service named ${evolution_agent_container_name} is already stopped."

    run is_service_up evolution_agent
    assert_failure
}

@test "Restarting the Evolution Agent when it's up-and-running" {
    local evolution_agent_port="$(get_config .services.evolution_agent.port)"

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    run das-cli evolution-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Stopping Evolution Agent service...
Evolution Agent service stopped
Starting Evolution Agent service...
Evolution Agent started on port ${evolution_agent_port}"

    run is_service_up evolution_agent
    assert_success
}

@test "Restarting the Evolution Agent when it's not up" {
    local evolution_agent_container_name="$(get_config .services.evolution_agent.container_name)"
    local evolution_agent_port="$(get_config .services.evolution_agent.port)"

    run das-cli evolution-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12700:12800

    assert_output "Stopping Evolution Agent service...
The Evolution Agent service named ${evolution_agent_container_name} is already stopped.
Starting Evolution Agent service...
Evolution Agent started on port ${evolution_agent_port}"

    run is_service_up evolution_agent
    assert_success
}
