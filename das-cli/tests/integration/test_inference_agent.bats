
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
    das-cli link-creation-agent start
    das-cli inference-agent stop
}

teardown() {
    das-cli inference-agent stop
    das-cli link-creation-agent stop
    das-cli attention-broker stop
    das-cli query-agent stop
    das-cli db stop
}

@test "Trying to start, stop and restart the Inference Agent with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli inference-agent $cmd

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Start Inference Agent when Link Creation Agent is not up" {
    das-cli link-creation-agent stop

    run das-cli inference-agent start
    assert_output "[31m[DockerContainerNotFoundError] 
Please start the required services before running 'inference-agent start'.
Run 'link-creation-agent start' to start the Link Creation Agent.[39m"

    run is_service_up link_creation_agent
    assert_failure

    run is_service_up inference_agent
    assert_failure
}

@test "Start Inference Agent when port is already in use" {
    local inference_agent_port="$(get_config .inference_agent.port)"

    run listen_port "${inference_agent_port}"
    assert_success

    run das-cli inference-agent start
    assert_output "Starting Inference Agent service...
[31m[DockerError] Port ${inference_agent_port} is already in use. Please stop the service that is currently using this port.[39m"

    run stop_listen_port "${inference_agent_port}"
    assert_success

    run is_service_up inference_agent
    assert_failure
}

@test "Starting the Inference Agent when it's already up" {
    local inference_agent_port="$(get_config .inference_agent.port)"

    das-cli inference-agent start

    run das-cli inference-agent start

    assert_output "Starting Inference Agent service...
Inference Agent is already running. It's listening on the ports ${inference_agent_port}, 8081, 8083, 8085"

    run is_service_up inference_agent

    assert_success
}

@test "Starting the Inference Agent" {
    local inference_agent_port="$(get_config .inference_agent.port)"

    run das-cli inference-agent start

    assert_output "Starting Inference Agent service...
Inference Agent started listening on the ports ${inference_agent_port}, 8081, 8083, 8085"

    run is_service_up inference_agent
    assert_success
}

@test "Stopping the Inference Agent when it's up-and-running" {
    local inference_agent_port="$(get_config .inference_agent.port)"

    das-cli inference-agent start

    run das-cli inference-agent stop

    assert_output "Stopping Inference Agent service...
Inference Agent service stopped"

    run is_service_up inference_agent
    assert_failure
}

@test "Stopping the Inference Agent when it's already stopped" {
    local inference_agent_container_name="$(get_config .inference_agent.container_name)"

    run das-cli inference-agent stop

    assert_output "Stopping Inference Agent service...
The Inference Agent service named ${inference_agent_container_name} is already stopped."

    run is_service_up inference_agent
    assert_failure
}

@test "Restarting the Inference Agent when it's up-and-running" {
    local inference_agent_port="$(get_config .inference_agent.port)"

    das-cli inference-agent start

    run das-cli inference-agent restart

    assert_output "Stopping Inference Agent service...
Inference Agent service stopped
Starting Inference Agent service...
Inference Agent started listening on the ports ${inference_agent_port}, 8081, 8083, 8085"

    run is_service_up inference_agent
    assert_success
}

@test "Restarting the Inference Agent when it's not up" {
    local inference_agent_container_name="$(get_config .inference_agent.container_name)"
    local inference_agent_port="$(get_config .inference_agent.port)"

    run das-cli inference-agent restart

    assert_output "Stopping Inference Agent service...
The Inference Agent service named ${inference_agent_container_name} is already stopped.
Starting Inference Agent service...
Inference Agent started listening on the ports ${inference_agent_port}, 8081, 8083, 8085"

    run is_service_up inference_agent
    assert_success
}
