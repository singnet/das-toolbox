#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db stop
    das-cli faas stop
}

teardown() {
    das-cli db stop
    das-cli faas stop
}

@test "Show logs for MongoDB, Redis and FaaS with unset configuration file" {
    local services=(mongodb redis faas)

    unset_config

    for service in "${services[@]}"; do
        run das-cli logs "$service"

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Trying to show logs for MongoDB before db is running" {

    run das-cli logs mongodb

    assert_output "[31m[DockerError] You need to run the server with command 'db start'[39m"

    run is_service_up mongodb

    assert_failure
}

@test "Trying to show logs for Redis before db is running" {

    run das-cli logs redis

    assert_output "[31m[DockerError] You need to run the server with command 'db start'[39m"

    run is_service_up redis

    assert_failure
}

@test "Trying to show logs for FaaS before db is running" {
    local openfaas_container_name="$(get_config .services.openfaas.container_name)"

    run das-cli logs faas

    assert_output "You need to run the server with command 'faas start'
[31m[DockerError] Service $openfaas_container_name is not running[39m"

    run is_service_up faas

    assert_failure
}

@test "Show logs for Redis, MongoDB and FaaS" {
    local services=(mongodb redis faas)

    das-cli db start
    das-cli faas start

    for service in "${services[@]}"; do
        run timeout 5s das-cli logs "${service}"

        assert_failure 124
    done
}

@test "Show DAS logs when the log file does not exist" {
    unset_log

    ! [ -f "$das_log_file" ]

    run timeout 5s das-cli logs das

    assert_output "No logs to show up here"
}

@test "Show logs for DAS" {

    run timeout 5s das-cli logs das

    assert_output "$(cat $das_log_file)"
}
