#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli attention-broker stop
}

@test "Trying to start, stop and restart the attention broker with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli attention-broker $cmd

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Start Attention Broker when port is already in use" {
    local attention_broker_port="$(get_config .services.attention_broker.port)"

    run listen_port "${attention_broker_port}"
    assert_success

    run das-cli attention-broker start
    assert_output "Starting Attention Broker service...
[31m[PortBindingError] Port ${attention_broker_port} on localhost are already in use.[39m"

    run stop_listen_port "${attention_broker_port}"
    assert_success

    run is_service_up attention_broker
    assert_failure
}

@test "Starting the Attention Broker when it's already up" {
    local attention_broker_port="$(get_config .services.attention_broker.port)"

    das-cli attention-broker start

    run das-cli attention-broker start

    assert_output "Starting Attention Broker service...
Attention Broker is already running. It's listening on port ${attention_broker_port}"

    run is_service_up attention_broker

    assert_success
}

@test "Starting the Attention Broker" {
    local attention_broker_port="$(get_config .services.attention_broker.port)"

    run das-cli attention-broker start

    assert_output "Starting Attention Broker service...
Attention Broker started on port ${attention_broker_port}"

    run is_service_up attention_broker

    assert_success
}

@test "Stopping the Attention Broker when it's up-and-running" {
    local attention_broker_port="$(get_config .services.attention_broker.port)"

    das-cli attention-broker start

    run das-cli attention-broker stop

    assert_output "Stopping Attention Broker service...
Attention Broker service stopped"

    run is_service_up attention_broker

    assert_failure
}

@test "Stopping the Attention Broker when it's already stopped" {
    local attention_broker_container_name="$(get_config .services.attention_broker.container_name)"

    run das-cli attention-broker stop

    assert_output "Stopping Attention Broker service...
The Attention Broker service named ${attention_broker_container_name} is already stopped."

    run is_service_up attention_broker

    assert_failure
}

@test "Restarting the Attention Broker when it's up-and-running" {
    local attention_broker_port="$(get_config .services.attention_broker.port)"

    das-cli attention-broker start

    run das-cli attention-broker restart

    assert_output "Stopping Attention Broker service...
Attention Broker service stopped
Starting Attention Broker service...
Attention Broker started on port ${attention_broker_port}"

    run is_service_up attention_broker

    assert_success
}

@test "Restarting the Attention Broker when it's not up" {
    local attention_broker_container_name="$(get_config .services.attention_broker.container_name)"
    local attention_broker_port="$(get_config .services.attention_broker.port)"

    run das-cli attention-broker restart

    assert_output "Stopping Attention Broker service...
The Attention Broker service named ${attention_broker_container_name} is already stopped.
Starting Attention Broker service...
Attention Broker started on port ${attention_broker_port}"

    run is_service_up attention_broker

    assert_success
}
