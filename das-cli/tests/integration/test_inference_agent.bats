#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli attention-broker start
    das-cli db start
    das-cli inference-agent stop
}

teardown() {
    das-cli inference-agent stop
    das-cli attention-broker stop
    das-cli db stop
}


@test "Fails to start the Inference Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12500:12600

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to stop the Inference Agent when configuration file is not set" {
    unset_config

    run das-cli inference-agent stop

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Fails to restart the Inference Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$peer_port" \
        --port-range 12500:12600

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Inference Agent when Attention Broker is not up" {
    das-cli attention-broker stop

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'inference-agent start'.
Run 'attention-broker start' to start the Attention Broker.[39m"

    run is_service_up attention_broker
    assert_failure

    run is_service_up inference_agent
    assert_failure
}

@test "Start Inference Agent when port is already in use" {
    local inference_agent_port="$(get_config .services.inference_agent.port)"

    run listen_port "${inference_agent_port}"
    assert_success

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600


    assert_output "Starting Inference Agent service...
[31m[PortBindingError] Port ${inference_agent_port} on localhost are already in use.[39m"

    run stop_listen_port "${inference_agent_port}"
    assert_success

    run is_service_up inference_agent
    assert_failure
}

@test "Starting the Inference Agent when it's already up" {
    local inference_agent_port="$(get_config .services.inference_agent.port)"

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    assert_output "Starting Inference Agent service...
Inference Agent is already running. It's listening on the ports ${inference_agent_port}"

    run is_service_up inference_agent

    assert_success
}

@test "Starting the Inference Agent" {
    local inference_agent_port="$(get_config .services.inference_agent.port)"

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    assert_output "Starting Inference Agent service...
Inference Agent started listening on the ports ${inference_agent_port}"

    run is_service_up inference_agent
    assert_success
}

@test "Stopping the Inference Agent when it's up-and-running" {
    local inference_agent_port="$(get_config .services.inference_agent.port)"

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    run das-cli inference-agent stop

    assert_output "Stopping Inference Agent service...
Inference Agent service stopped"

    run is_service_up inference_agent
    assert_failure
}

@test "Stopping the Inference Agent when it's already stopped" {
    local inference_agent_container_name="$(get_config .services.inference_agent.container_name)"

    run das-cli inference-agent stop

    assert_output "Stopping Inference Agent service...
The Inference Agent service named ${inference_agent_container_name} is already stopped."

    run is_service_up inference_agent
    assert_failure
}

@test "Restarting the Inference Agent when it's up-and-running" {
    local inference_agent_port="$(get_config .services.inference_agent.port)"

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    assert_output "Stopping Inference Agent service...
Inference Agent service stopped
Starting Inference Agent service...
Inference Agent started listening on the ports ${inference_agent_port}"

    run is_service_up inference_agent
    assert_success
}

@test "Restarting the Inference Agent when it's not up" {
    local inference_agent_container_name="$(get_config .services.inference_agent.container_name)"
    local inference_agent_port="$(get_config .services.inference_agent.port)"

    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600

    assert_output "Stopping Inference Agent service...
The Inference Agent service named ${inference_agent_container_name} is already stopped.
Starting Inference Agent service...
Inference Agent started listening on the ports ${inference_agent_port}"

    run is_service_up inference_agent
    assert_success
}
