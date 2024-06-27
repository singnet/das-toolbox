#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {

    use_config "redis_cluster"

    local redis_node2_ip="$(get_config .redis.nodes.1.ip)"
    local redis_node2_username="$(get_config .redis.nodes.1.username)"

    local redis_node3_ip="$(get_config .redis.nodes.2.ip)"
    local redis_node3_username="$(get_config .redis.nodes.2.username)"

    set_config ".redis.nodes.0.username" "$current_user"
    set_config ".redis.nodes.1.context" "$(set_ssh_context ${redis_node2_username} ${redis_node2_ip})"
    set_config ".redis.nodes.2.context" "$(set_ssh_context ${redis_node2_username} ${redis_node2_ip})"

    das-cli db stop
}

teardown() {
    das-cli db stop
}

# bats test_tags=redis:cluster
@test "Starting db with redis cluster" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_port="$(get_config ".redis.port")"

    local redis_node1_context="$(get_config ".redis.nodes.0.context")"
    local redis_node1_ip="$(get_config ".redis.nodes.0.ip")"
    local redis_node1_username="$(get_config ".redis.nodes.0.username")"

    local redis_node2_context="$(get_config ".redis.nodes.1.context")"
    local redis_node2_ip="$(get_config ".redis.nodes.1.ip")"
    local redis_node2_username="$(get_config ".redis.nodes.1.username")"

    local redis_node3_context="$(get_config ".redis.nodes.2.context")"
    local redis_node3_ip="$(get_config ".redis.nodes.2.ip")"
    local redis_node3_username="$(get_config ".redis.nodes.2.username")"

    run timeout 5m das-cli db start

    assert_success

    assert_output "Stopping redis service...
Redis has started successfully on port ${redis_port} at ${redis_node1_ip}, operating under the user ${redis_node2_username}.
Redis has started successfully on port ${redis_port} at ${redis_node1_ip}, operating under the user ${redis_node2_username}.
Redis has started successfully on port ${redis_port} at ${redis_node1_ip}, operating under the user ${redis_node2_username}.
MongoDB started on port ${mongodb_port}"

    unset_ssh_context "$redis_context_02"
    unset_ssh_context "$redis_context_03"

    run exec_cmd_on_service "redis" "redis-cli -c CLUSTER NODES | wc -l"

    assert_output "3"
}
