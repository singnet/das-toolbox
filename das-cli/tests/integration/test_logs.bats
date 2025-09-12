#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db stop
    das-cli attention-broker stop
    das-cli query-agent stop
    das-cli link-creation-agent stop
    das-cli inference-agent stop
    das-cli evolution-agent stop
}

teardown() {
    das-cli db stop
    das-cli attention-broker stop
    das-cli query-agent stop
    das-cli link-creation-agent stop
    das-cli inference-agent stop
    das-cli evolution-agent stop
}

@test "Show logs for MongoDB and Redis with unset configuration file" {
    local services=(mongodb redis)

    unset_config

    for service in "${services[@]}"; do
        run das-cli logs "$service"

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Trying to show logs for MongoDB before db is running" {

    run das-cli logs mongodb

    assert_output "[31m[DockerContainerNotFoundError] MongoDB is not running. Please start it with 'das-cli db start' before viewing logs.[39m"

    run is_service_up mongodb

    assert_failure
}

@test "Trying to show logs for Redis before db is running" {

    run das-cli logs redis

    assert_output "[31m[DockerContainerNotFoundError] Redis is not running. Please start it with 'das-cli db start' before viewing logs.[39m"

    run is_service_up redis

    assert_failure
}

@test "Show logs for Redis and MongoDB" {
    local services=(mongodb redis)

    das-cli db start

    for service in "${services[@]}"; do
        run timeout 5s das-cli logs "${service}"

        assert_failure 124
    done
}

@test "Trying to show logs for attention broker before it is running" {
    local attention_broker_container_name="$(get_config .services.attention_broker.container_name)"

    run das-cli logs attention-broker

    assert_output "[31m[DockerContainerNotFoundError] Attention broker is not running. Please start it with 'das-cli attention-broker start' before viewing logs.[39m"

    run is_service_up attention-broker

    assert_failure
}

@test "Show logs for attention broker" {
    das-cli attention-broker start
    run timeout 5s das-cli logs attention-broker

    assert_failure 124
}


@test "Trying to show logs for query agent before it is running" {
    local query_agent_container_name="$(get_config .services.query_agent.container_name)"

    run das-cli logs query-agent

    assert_output "[31m[DockerContainerNotFoundError] Query agent is not running. Please start it with 'das-cli query-agent start' before viewing logs.[39m"

    run is_service_up query-agent

    assert_failure
}

@test "Show logs for query agent" {
    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100

    run timeout 5s das-cli logs query-agent

    assert_failure 124
}

@test "Trying to show logs for link creation agent before it is running" {
    local link_creation_agent_container_name="$(get_config .services.link_creation_agent.container_name)"

    run das-cli logs link-creation-agent

    assert_output "[31m[DockerContainerNotFoundError] Link creation agent is not running. Please start it with 'das-cli link-creation-agent start' before viewing logs.[39m"

    run is_service_up link-creation-agent

    assert_failure
}

@test "Show logs for link creation agent" {
    das-cli attention-broker start
    das-cli db start
    das-cli query-agent start --port-range 12000:12100
    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12300:12400

    run timeout 5s das-cli logs link-creation-agent

    assert_failure 124
}

@test "Trying to show logs for inference agent before it is running" {
    local inference_agent_container_name="$(get_config .services.inference_agent.container_name)"

    run das-cli logs inference-agent

    assert_output "[31m[DockerContainerNotFoundError] Inference agent is not running. Please start it with 'das-cli inference-agent start' before viewing logs.[39m"

    run is_service_up inference-agent

    assert_failure
}

@test "Show logs for inference agent" {
    das-cli attention-broker start
    das-cli db start

    das-cli query-agent start --port-range 12000:12100
    das-cli link-creation-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12300:12400

    das-cli inference-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12500:12600


    run timeout 5s das-cli logs inference-agent

    assert_failure 124
}

@test "Trying to show logs for evolution agent before it is running" {
    local evolution_agent_container_name="$(get_config .services.evolution_agent.container_name)"

    run das-cli logs evolution-agent

    assert_output "[31m[DockerContainerNotFoundError] Evolution Agent is not running. Please start it with 'das-cli evolution-agent start' before viewing logs.[39m"

    run is_service_up evolution-agent

    assert_failure
}

@test "Show logs for evolution agent" {
    das-cli db start
    das-cli attention-broker start
    das-cli query-agent start --port-range 12000:12100

    das-cli evolution-agent start \
        --peer-hostname localhost \
        --peer-port "$(get_config ".services.query_agent.port")" \
        --port-range 12300:12400

    run timeout 5s das-cli logs evolution-agent

    assert_failure 124
}


@test "Show DAS logs when the log file does not exist" {
    unset_log

    ! [ -f "$das_log_file" ]

    run timeout 5s das-cli logs das

    assert_output "No logs to show up here"
}

@test "Show logs for DAS" {
    set_log

    run timeout 5s das-cli logs das

    assert_output "$(cat $das_log_file)"
}
