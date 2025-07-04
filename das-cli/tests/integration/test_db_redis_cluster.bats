#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {

    use_config "redis_cluster"

    local redis_node2_ip="$(get_config .redis.nodes[1].ip)"
    local redis_node2_username="$(get_config .redis.nodes[1].username)"

    local redis_node3_ip="$(get_config .redis.nodes[2].ip)"
    local redis_node3_username="$(get_config .redis.nodes[2].username)"

    set_config ".redis.nodes[0].username" "\"$current_user\""
    set_config ".redis.nodes[1].context" "\"$(set_ssh_context "$redis_node2_username" "$redis_node2_ip")\""
    set_config ".redis.nodes[2].context" "\"$(set_ssh_context "$redis_node3_username" "$redis_node3_ip")\""

    das-cli db stop
}

teardown() {
    das-cli db stop
}

# bats test_tags=cluster
@test "Starting db with redis cluster" {
    local mongodb_port="$(get_config ".services.mongodb.port")"
    local redis_port="$(get_config ".services.redis.port")"

    local redis_node1_context="$(get_config ".services.redis.nodes[0].context")"
    local redis_node1_ip="$(get_config ".services.redis.nodes[0].ip")"
    local redis_node1_username="$(get_config ".services.redis.nodes[0].username")"

    local redis_node2_context="$(get_config ".services.redis.nodes[1].context")"
    local redis_node2_ip="$(get_config ".services.redis.nodes[1].ip")"
    local redis_node2_username="$(get_config ".services.redis.nodes[1].username")"

    local redis_node3_context="$(get_config ".services.redis.nodes[2].context")"
    local redis_node3_ip="$(get_config ".services.redis.nodes[2].ip")"
    local redis_node3_username="$(get_config ".services.redis.nodes[2].username")"

    run timeout 5m das-cli db start

    assert_success

    assert_line --partial "Starting Redis service..."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node1_ip}, operating under the server user ${redis_node1_username}."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node2_ip}, operating under the server user ${redis_node2_username}."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node3_ip}, operating under the server user ${redis_node3_username}."

    unset_ssh_context "$redis_context_02"
    unset_ssh_context "$redis_context_03"

    run exec_cmd_on_service "redis" "redis-cli -c CLUSTER NODES | wc -l"

    assert [ "$(clean_string $output)" == "3" ]

    run is_service_up redis
    assert_success
}

# bats test_tags=cluster
@test "Stopping db with redis cluster" {
    local redis_port="$(get_config ".services.redis.port")"

    local redis_node1_context="$(get_config ".services.redis.nodes[0].context")"
    local redis_node1_ip="$(get_config ".services.redis.nodes[0].ip")"
    local redis_node1_username="$(get_config ".services.redis.nodes[0].username")"

    local redis_node2_context="$(get_config ".services.redis.nodes[1].context")"
    local redis_node2_ip="$(get_config ".services.redis.nodes[1].ip")"
    local redis_node2_username="$(get_config ".services.redis.nodes[1].username")"

    local redis_node3_context="$(get_config ".services.redis.nodes[2].context")"
    local redis_node3_ip="$(get_config ".services.redis.nodes[2].ip")"
    local redis_node3_username="$(get_config ".services.redis.nodes[2].username")"

    das-cli db start

    run timeout 5m das-cli db stop

    assert_success


    assert_line --partial "Stopping Redis service..."
    assert_line --partial "The Redis service at ${redis_node2_ip} has been stopped by the server user ${redis_node2_username}"
    assert_line --partial "The Redis service at ${redis_node1_ip} has been stopped by the server user ${redis_node1_username}"
    assert_line --partial "The Redis service at ${redis_node3_ip} has been stopped by the server user ${redis_node3_username}"

    unset_ssh_context "$redis_context_02"
    unset_ssh_context "$redis_context_03"

    run is_service_up redis
    assert_failure

}

# bats test_tags=cluster
@test "Restarting db with redis cluster after cluster is up" {
    local mongodb_port="$(get_config ".services.mongodb.port")"
    local redis_port="$(get_config ".services.redis.port")"

    local redis_node1_context="$(get_config ".services.redis.nodes[0].context")"
    local redis_node1_ip="$(get_config ".services.redis.nodes[0].ip")"
    local redis_node1_username="$(get_config ".services.redis.nodes[0].username")"

    local redis_node2_context="$(get_config ".services.redis.nodes[1].context")"
    local redis_node2_ip="$(get_config ".services.redis.nodes[1].ip")"
    local redis_node2_username="$(get_config ".services.redis.nodes[1].username")"

    local redis_node3_context="$(get_config ".services.redis.nodes[2].context")"
    local redis_node3_ip="$(get_config ".services.redis.nodes[2].ip")"
    local redis_node3_username="$(get_config ".services.redis.nodes[2].username")"

    das-cli db start

    run timeout 5m das-cli db restart

    assert_success

    assert_line --partial "Stopping Redis service..."
    assert_line --partial "The Redis service at ${redis_node2_ip} has been stopped by the server user ${redis_node2_username}"
    assert_line --partial "The Redis service at ${redis_node1_ip} has been stopped by the server user ${redis_node1_username}"
    assert_line --partial "The Redis service at ${redis_node3_ip} has been stopped by the server user ${redis_node3_username}"

    assert_line --partial "Starting Redis service..."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node1_ip}, operating under the server user ${redis_node1_username}."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node2_ip}, operating under the server user ${redis_node2_username}."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node3_ip}, operating under the server user ${redis_node3_username}."

    unset_ssh_context "$redis_context_02"
    unset_ssh_context "$redis_context_03"

    run exec_cmd_on_service "redis" "redis-cli -c CLUSTER NODES | wc -l"

    assert [ "$(clean_string $output)" == "3" ]

    run is_service_up redis
    assert_success
}

# bats test_tags=cluster
@test "Restarting db with redis cluster before cluster is up" {
    local mongodb_port="$(get_config ".services.mongodb.port")"
    local mongodb_container_name="$(get_config ".services.mongodb.container_name")"
    local redis_port="$(get_config ".services.redis.port")"
    local redis_container_name="$(get_config ".services.redis.container_name")"

    local redis_node1_context="$(get_config ".services.redis.nodes[0].context")"
    local redis_node1_ip="$(get_config ".services.redis.nodes[0].ip")"
    local redis_node1_username="$(get_config ".services.redis.nodes[0].username")"

    local redis_node2_context="$(get_config ".services.redis.nodes[1].context")"
    local redis_node2_ip="$(get_config ".services.redis.nodes[1].ip")"
    local redis_node2_username="$(get_config ".services.redis.nodes[1].username")"

    local redis_node3_context="$(get_config ".services.redis.nodes[2].context")"
    local redis_node3_ip="$(get_config ".services.redis.nodes[2].ip")"
    local redis_node3_username="$(get_config ".services.redis.nodes[2].username")"

    run timeout 5m das-cli db restart

    assert_success


    assert_line --partial "Stopping Redis service..."
    assert_line --partial "The Redis service named ${redis_container_name} at ${redis_node1_ip} is already stopped."
    assert_line --partial "The Redis service named ${redis_container_name} at ${redis_node2_ip} is already stopped."
    assert_line --partial "The Redis service named ${redis_container_name} at ${redis_node3_ip} is already stopped."

    assert_line --partial "Starting Redis service..."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node1_ip}, operating under the server user ${redis_node1_username}."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node2_ip}, operating under the server user ${redis_node2_username}."
    assert_line --partial "Redis has started successfully on port ${redis_port} at ${redis_node3_ip}, operating under the server user ${redis_node3_username}."

    unset_ssh_context "$redis_context_02"
    unset_ssh_context "$redis_context_03"

    run exec_cmd_on_service "redis" "redis-cli -c CLUSTER NODES | wc -l"

    assert [ "$(clean_string $output)" == "3" ]

    run is_service_up redis
    assert_success
}
