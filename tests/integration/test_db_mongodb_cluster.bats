#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {

    use_config "mongodb_cluster"

    local mongodb_node2_ip="$(get_config .mongodb.nodes[1].ip)"
    local mongodb_node2_username="$(get_config .mongodb.nodes[1].username)"

    local mongodb_node3_ip="$(get_config .mongodb.nodes[2].ip)"
    local mongodb_node3_username="$(get_config .mongodb.nodes[2].username)"

    set_config ".mongodb.nodes[0].username" "\"$current_user\""
    set_config ".mongodb.nodes[1].context" "\"$(set_ssh_context "$mongodb_node2_username" "$mongodb_node2_ip")\""
    set_config ".mongodb.nodes[2].context" "\"$(set_ssh_context "$mongodb_node3_username" "$mongodb_node3_ip")\""

    das-cli db stop
}

teardown() {
    das-cli db stop
}

# bats test_tags=cluster
@test "Starting db with mongodb cluster" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local mongodb_username="$(get_config ".mongodb.username")"
    local mongodb_password="$(get_config ".mongodb.password")"

    local mongodb_node1_context="$(get_config ".mongodb.nodes[0].context")"
    local mongodb_node1_ip="$(get_config ".mongodb.nodes[0].ip")"
    local mongodb_node1_username="$(get_config ".mongodb.nodes[0].username")"

    local mongodb_node2_context="$(get_config ".mongodb.nodes[1].context")"
    local mongodb_node2_ip="$(get_config ".mongodb.nodes[1].ip")"
    local mongodb_node2_username="$(get_config ".mongodb.nodes[1].username")"

    local mongodb_node3_context="$(get_config ".mongodb.nodes[2].context")"
    local mongodb_node3_ip="$(get_config ".mongodb.nodes[2].ip")"
    local mongodb_node3_username="$(get_config ".mongodb.nodes[2].username")"

    run timeout 5m das-cli db start

    assert_success

    assert_line --partial "Starting MongoDB service..."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node1_ip}, operating under the server user ${mongodb_node1_username}."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node2_ip}, operating under the server user ${mongodb_node2_username}."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node3_ip}, operating under the server user ${mongodb_node3_username}."

    unset_ssh_context "$mongodb_context_02"
    unset_ssh_context "$mongodb_context_03"

    run exec_cmd_on_service "mongodb" "mongosh -u ${mongodb_username} -p ${mongodb_password} --eval 'rs.status().members.filter(member => member.state === 1 || member.state === 2).length' | tail -n 1"

    assert [ "$(clean_string $output)" == "3" ]

    run is_service_up mongodb
    assert_success
}

# bats test_tags=cluster
@test "Stopping db with mongodb cluster" {
    local mongodb_port="$(get_config ".mongodb.port")"

    local mongodb_node1_context="$(get_config ".mongodb.nodes[0].context")"
    local mongodb_node1_ip="$(get_config ".mongodb.nodes[0].ip")"
    local mongodb_node1_username="$(get_config ".mongodb.nodes[0].username")"

    local mongodb_node2_context="$(get_config ".mongodb.nodes[1].context")"
    local mongodb_node2_ip="$(get_config ".mongodb.nodes[1].ip")"
    local mongodb_node2_username="$(get_config ".mongodb.nodes[1].username")"

    local mongodb_node3_context="$(get_config ".mongodb.nodes[2].context")"
    local mongodb_node3_ip="$(get_config ".mongodb.nodes[2].ip")"
    local mongodb_node3_username="$(get_config ".mongodb.nodes[2].username")"

    das-cli db start

    run timeout 5m das-cli db stop

    assert_success


    assert_line --partial "Stopping MongoDB service..."
    assert_line --partial "The MongoDB service at ${mongodb_node2_ip} has been stopped by the server user ${mongodb_node2_username}"
    assert_line --partial "The MongoDB service at ${mongodb_node1_ip} has been stopped by the server user ${mongodb_node1_username}"
    assert_line --partial "The MongoDB service at ${mongodb_node3_ip} has been stopped by the server user ${mongodb_node3_username}"

    unset_ssh_context "$mongodb_context_02"
    unset_ssh_context "$mongodb_context_03"

    run is_service_up mongodb
    assert_failure

}

# bats test_tags=cluster
@test "Restarting db with mongodb cluster after cluster is up" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local mongodb_username="$(get_config ".mongodb.username")"
    local mongodb_password="$(get_config ".mongodb.password")"

    local mongodb_node1_context="$(get_config ".mongodb.nodes[0].context")"
    local mongodb_node1_ip="$(get_config ".mongodb.nodes[0].ip")"
    local mongodb_node1_username="$(get_config ".mongodb.nodes[0].username")"

    local mongodb_node2_context="$(get_config ".mongodb.nodes[1].context")"
    local mongodb_node2_ip="$(get_config ".mongodb.nodes[1].ip")"
    local mongodb_node2_username="$(get_config ".mongodb.nodes[1].username")"

    local mongodb_node3_context="$(get_config ".mongodb.nodes[2].context")"
    local mongodb_node3_ip="$(get_config ".mongodb.nodes[2].ip")"
    local mongodb_node3_username="$(get_config ".mongodb.nodes[2].username")"

    das-cli db start

    run timeout 5m das-cli db restart

    assert_success

    assert_line --partial "Stopping MongoDB service..."
    assert_line --partial "The MongoDB service at ${mongodb_node2_ip} has been stopped by the server user ${mongodb_node2_username}"
    assert_line --partial "The MongoDB service at ${mongodb_node1_ip} has been stopped by the server user ${mongodb_node1_username}"
    assert_line --partial "The MongoDB service at ${mongodb_node3_ip} has been stopped by the server user ${mongodb_node3_username}"

    assert_line --partial "Starting MongoDB service..."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node1_ip}, operating under the server user ${mongodb_node1_username}."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node2_ip}, operating under the server user ${mongodb_node2_username}."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node3_ip}, operating under the server user ${mongodb_node3_username}."

    unset_ssh_context "$mongodb_context_02"
    unset_ssh_context "$mongodb_context_03"

    run exec_cmd_on_service "mongodb" "mongosh -u ${mongodb_username} -p ${mongodb_password} --eval 'rs.status().members.filter(member => member.state === 1 || member.state === 2).length' | tail -n 1"

    assert [ "$(clean_string $output)" == "3" ]

    run is_service_up mongodb
    assert_success
}

# bats test_tags=cluster
@test "Restarting db with mongodb cluster before cluster is up" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local mongodb_username="$(get_config ".mongodb.username")"
    local mongodb_password="$(get_config ".mongodb.password")"
    local mongodb_container_name="$(get_config ".mongodb.container_name")"
    local mongodb_container_name="$(get_config ".mongodb.container_name")"

    local mongodb_node1_context="$(get_config ".mongodb.nodes[0].context")"
    local mongodb_node1_ip="$(get_config ".mongodb.nodes[0].ip")"
    local mongodb_node1_username="$(get_config ".mongodb.nodes[0].username")"

    local mongodb_node2_context="$(get_config ".mongodb.nodes[1].context")"
    local mongodb_node2_ip="$(get_config ".mongodb.nodes[1].ip")"
    local mongodb_node2_username="$(get_config ".mongodb.nodes[1].username")"

    local mongodb_node3_context="$(get_config ".mongodb.nodes[2].context")"
    local mongodb_node3_ip="$(get_config ".mongodb.nodes[2].ip")"
    local mongodb_node3_username="$(get_config ".mongodb.nodes[2].username")"

    run timeout 5m das-cli db restart

    assert_success


    assert_line --partial "Stopping MongoDB service..."
    assert_line --partial "The MongoDB service named ${mongodb_container_name} at ${mongodb_node1_ip} is already stopped."
    assert_line --partial "The MongoDB service named ${mongodb_container_name} at ${mongodb_node2_ip} is already stopped."
    assert_line --partial "The MongoDB service named ${mongodb_container_name} at ${mongodb_node3_ip} is already stopped."

    assert_line --partial "Starting MongoDB service..."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node1_ip}, operating under the server user ${mongodb_node1_username}."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node2_ip}, operating under the server user ${mongodb_node2_username}."
    assert_line --partial "MongoDB has started successfully on port ${mongodb_port} at ${mongodb_node3_ip}, operating under the server user ${mongodb_node3_username}."

    unset_ssh_context "$mongodb_context_02"
    unset_ssh_context "$mongodb_context_03"

    run exec_cmd_on_service "mongodb" "mongosh -u ${mongodb_username} -p ${mongodb_password} --eval 'rs.status().members.filter(member => member.state === 1 || member.state === 2).length' | tail -n 1"

    assert [ "$(clean_string $output)" == "3" ]

    run is_service_up mongodb
    assert_success
}
