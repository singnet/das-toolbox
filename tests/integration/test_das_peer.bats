#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli das-peer stop
    das-cli db stop
}

@test "Trying to start, stop and restart db with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli db $cmd

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Starting DAS Peer when db is not up" {
    local mongodb_container_name="$(get_config ".mongodb.container_name")"
    local redis_container_name="$(get_config ".redis.container_name")"

    run das-cli das-peer start

    assert_output "$mongodb_container_name is not running
$redis_container_name is not running
[31m[DockerContainerNotFoundError] 
Please use 'db start' to start required services before running 'das-peer start'.[39m"

    run is_service_up redis
    assert_failure

    run is_service_up mongodb
    assert_failure

    run is_service_up das-peer
    assert_failure
}

@test "Starting DAS Peer command" {
    local mongodb_container_name="$(get_config ".mongodb.container_name")"
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_container_name="$(get_config ".redis.container_name")"
    local redis_port="$(get_config .redis.port)"
    local das_peer_port="$(get_config .das_peer.port)"

    das-cli db start

    run das-cli das-peer start

    assert_output "$mongodb_container_name is running on port $mongodb_port
$redis_container_name is running on port $redis_port
Starting DAS Peer server...
DAS Peer is runnig on port $das_peer_port"

    sleep 15s

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success

    run is_service_up das_peer
    assert_success
}

@test "It should display an error message if the database is unavailable when attempting to start das-peer" {
    local mongodb_container_name="$(get_config ".mongodb.container_name")"
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_container_name="$(get_config ".redis.container_name")"
    local redis_port="$(get_config .redis.port)"
    local das_peer_port="$(get_config .das_peer.port)"

    run is_service_up redis
    assert_failure

    run is_service_up mongodb
    assert_failure

    run das-cli das-peer start

    assert_output "$mongodb_container_name is not running
$redis_container_name is not running
[31m[DockerContainerNotFoundError] 
Please use 'db start' to start required services before running 'das-peer start'.[39m"

    run is_service_up das_peer
    assert_failure
}
