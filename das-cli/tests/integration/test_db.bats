#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

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

@test "Starting mongodb and redis standalone" {
    local mongodb_port="$(get_config .services.mongodb.port)"
    local mongodb_node1_username="$(get_config .services.mongodb.nodes[0].username)"
    local mongodb_node1_ip="$(get_config .services.mongodb.nodes[0].ip)"
    local redis_port="$(get_config .services.redis.port)"
    local redis_node1_username="$(get_config .services.redis.nodes[0].username)"
    local redis_node1_ip="$(get_config .services.redis.nodes[0].ip)"

    run das-cli db start

    assert_output "Starting Redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the server user ${redis_node1_username}.
Starting MongoDB service...
MongoDB has started successfully on port ${mongodb_port} at localhost, operating under the server user ${mongodb_node1_username}."

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should gives up a warning when db is already up" {
    local mongodb_port="$(get_config .services.mongodb.port)"
    local mongodb_node1_username="$(get_config .services.mongodb.nodes[0].username)"
    local mongodb_node1_ip="$(get_config .services.mongodb.nodes[0].ip)"
    local redis_port="$(get_config .services.redis.port)"
    local redis_node1_username="$(get_config .services.redis.nodes[0].username)"
    local redis_node1_ip="$(get_config .services.redis.nodes[0].ip)"

    das-cli db start

    run das-cli db start

    assert_output "Starting Redis service...
Redis is already running. It is currently listening on port ${redis_port} at localhost under the server user ${redis_node1_username}.
Starting MongoDB service...
MongoDB is already running. It is currently listening on port ${mongodb_port} at localhost under the server user ${mongodb_node1_username}."

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should restart even though services are stopped" {
    local mongodb_port="$(get_config ".services.mongodb.port")"
    local mongodb_node1_username="$(get_config ".services.mongodb.nodes[0].username")"
    local mongodb_node1_ip="$(get_config ".services.mongodb.nodes[0].ip")"
    local mongodb_container_name="$(get_config .services.mongodb.container_name)"

    local redis_port="$(get_config .services.redis.port)"
    local redis_node1_username="$(get_config ".services.redis.nodes[0].username")"
    local redis_node1_ip="$(get_config ".services.redis.nodes[0].ip")"
    local redis_container_name="$(get_config .services.redis.container_name)"

    run das-cli db restart

    assert_output "Stopping Redis service...
The Redis service named ${redis_container_name} at localhost is already stopped.
Stopping MongoDB service...
The MongoDB service named ${mongodb_container_name} at localhost is already stopped.
Starting Redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the server user ${redis_node1_username}.
Starting MongoDB service...
MongoDB has started successfully on port ${mongodb_port} at localhost, operating under the server user ${mongodb_node1_username}."

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should restart db successfully when db is already up" {
    local mongodb_port="$(get_config .services.mongodb.port)"
    local mongodb_node1_username="$(get_config .services.mongodb.nodes[0].username)"
    local redis_port="$(get_config .services.redis.port)"
    local redis_node1_username="$(get_config .services.redis.nodes[0].username)"

    das-cli db start

    run das-cli db restart

    assert_output "Stopping Redis service...
The Redis service at localhost has been stopped by the server user ${redis_node1_username}
Stopping MongoDB service...
The MongoDB service at localhost has been stopped by the server user ${mongodb_node1_username}
Starting Redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the server user ${redis_node1_username}.
Starting MongoDB service...
MongoDB has started successfully on port ${mongodb_port} at localhost, operating under the server user ${mongodb_node1_username}."

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should stop db successfully" {
    local mongodb_node1_username="$(get_config ".services.mongodb.nodes[0].username")"
    local redis_node1_username="$(get_config ".services.redis.nodes[0].username")"

    das-cli db start &>/dev/null

    run das-cli db stop

    assert_output "Stopping Redis service...
The Redis service at localhost has been stopped by the server user ${redis_node1_username}
Stopping MongoDB service...
The MongoDB service at localhost has been stopped by the server user ${mongodb_node1_username}"

    run is_service_up redis
    assert_failure

    run is_service_up mongodb
    assert_failure
}

@test "It should warns up when db is already stopped" {
    local redis_container_name="$(get_config .services.redis.container_name)"
    local mongodb_container_name="$(get_config .services.mongodb.container_name)"

    run das-cli db stop

    assert_output "Stopping Redis service...
The Redis service named ${redis_container_name} at localhost is already stopped.
Stopping MongoDB service...
The MongoDB service named ${mongodb_container_name} at localhost is already stopped."

    run is_service_up redis
    assert_failure

    run is_service_up mongodb
    assert_failure
}

@test "Should count atoms with verbose mode enabled" {
    das-cli db restart &>/dev/null

    das-cli metta load "$test_fixtures_dir/metta/animals.metta" &>/dev/null

    run das-cli db count-atoms --verbose

    assert_success

    assert_regex "$output" '(MongoDB\s.*:\s[0-9]+)'
    local mongodb_count=$(grep -oE 'MongoDB\s.*:\s[0-9]+' <<<"$output" | wc -l)

    [ "$mongodb_count" -eq 3 ]

    assert_regex "$output" '(Redis\s.*:\s[0-9]+)'
    local redis_count=$(grep -oE 'Redis\s.*:\s[0-9]+' <<<"$output" | wc -l)

    [ "$redis_count" -eq 5 ]
}

@test "Should count atoms with verbose mode disabled" {
    das-cli db restart &>/dev/null

    das-cli metta load "$test_fixtures_dir/metta/animals.metta" &>/dev/null

    run das-cli db count-atoms

    assert_success
    assert_regex "$output" '([0-9]+)'
}

@test "Should count atoms with verbose mode enabled and empty database" {
    das-cli db restart &>/dev/null

    run das-cli db count-atoms --verbose

    assert_success
    assert_output "MongoDB: No collections found (0)
Redis: No keys found (0)"
}

@test "Should count atoms with verbose mode disabled and empty database" {
    das-cli db restart &>/dev/null

    run das-cli db count-atoms

    assert_success
    assert_output "0"
}

@test "Should count atoms with database disabled" {
    local redis_container_name="$(get_config .services.redis.container_name)"
    local mongodb_container_name="$(get_config .services.mongodb.container_name)"

    run das-cli db count-atoms

    assert_success "${mongodb_container_name} is not running
${redis_container_name} is not running
[31m[DockerContainerNotFoundError]
Please use 'db start' to start required services before running 'db count-atoms'.[39m"
}
