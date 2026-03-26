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

    inference_agent_endpoint=$(get_config .agents.inference.endpoint)
    inference_agent_port=$(extract_port "$inference_agent_endpoint")

    query_agent_endpoint=$(get_config .agents.query.endpoint)
    query_agent_port=$(extract_port "$inference_agent_endpoint")

    service_name=das-inference-agent-40004
}

teardown() {
    das-cli inference-agent stop
    das-cli attention-broker stop
}


@test "Fails to start the Inference Agent when configuration file is not set" {
    unset_config

    local peer_port="12000"

    run das-cli inference-agent start \
        --peer-hostname 0.0.0.0 \
        --peer-port $query_agent_port \
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
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Start Inference Agent when Attention Broker is not up" {
    das-cli attention-broker stop

    run das-cli inference-agent start \
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'inference-agent start'.
Run 'attention-broker start' to start the Attention Broker.[39m"

    run is_service_up das-attention-broker-40001
    assert_failure

    run is_service_up $service_name
    assert_failure
}

@test "Start Inference Agent when port is already in use" {

    run listen_port "$inference_agent_port"
    assert_success

    run das-cli inference-agent start \
        --peer-hostname 0.0.0.0 \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600


    assert_output "Starting Inference Agent service...
[31m[PortBindingError] Port ${inference_agent_port} on localhost are already in use.[39m"

    run stop_listen_port "$inference_agent_port"
    assert_success

    run is_service_up $service_name
    assert_failure
}

@test "Starting the Inference Agent when it's already up" {

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output "Starting Inference Agent service...
Inference Agent is already running. It's listening on the ports $inference_agent_port"

    run is_service_up $service_name

    assert_success
}

@test "Starting the Inference Agent" {

    run das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output "Starting Inference Agent service...
Inference Agent started listening on the ports $inference_agent_port"

    run is_service_up $service_name
    assert_success
}

@test "Stopping the Inference Agent when it's up-and-running" {

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    run das-cli inference-agent stop

    assert_output "Stopping Inference Agent service...
Inference Agent service stopped"

    run is_service_up $service_name
    assert_failure
}

@test "Stopping the Inference Agent when it's already stopped" {
    run das-cli inference-agent stop

    assert_output "Stopping Inference Agent service...
The Inference Agent service named $service_name is already stopped."

    run is_service_up $service_name
    assert_failure
}

@test "Restarting the Inference Agent when it's up-and-running" {
    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output "Stopping Inference Agent service...
Inference Agent service stopped
Starting Inference Agent service...
Inference Agent started listening on the ports $inference_agent_port"

    run is_service_up $service_name
    assert_success
}

@test "Restarting the Inference Agent when it's not up" {
    run das-cli inference-agent restart \
        --peer-hostname localhost \
        --peer-port "$query_agent_port" \
        --port-range 12500:12600

    assert_output "Stopping Inference Agent service...
The Inference Agent service named $service_name is already stopped.
Starting Inference Agent service...
Inference Agent started listening on the ports $inference_agent_port"

    run is_service_up $service_name
    assert_success
}
