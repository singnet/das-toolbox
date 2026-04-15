#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"
    das-cli db stop
}

@test "Trying to start, stop and restart db with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli db "$cmd"

        assert_output --partial "$FILE_NOT_FOUND_ERROR"
    done
}

@test "Starting mongodb and redis standalone" {
    local mongodb_port="$(extract_port "$(get_config .atomdb.mongodb.endpoint)")"
    local mongodb_user="$(get_config .atomdb.mongodb.nodes[0].username)"

    local redis_port="$(extract_port "$(get_config .atomdb.redis.endpoint)")"
    local redis_user="$(get_config .atomdb.redis.nodes[0].username)"

    run das-cli db start

    assert_output --partial "Starting Redis service"
    assert_output --partial "Redis has started successfully"
    assert_output --partial "${redis_port}"
    assert_output --partial "${redis_user}"

    assert_output --partial "Starting MongoDB service"
    assert_output --partial "MongoDB has started successfully"
    assert_output --partial "${mongodb_port}"
    assert_output --partial "${mongodb_user}"

    run is_service_up das-cli-redis-40020
    assert_success

    run is_service_up das-cli-mongodb-40021
    assert_success
}

@test "It should gives up a warning when db is already up" {
    local mongodb_port="$(extract_port "$(get_config .atomdb.mongodb.endpoint)")"
    local mongodb_user="$(get_config .atomdb.mongodb.nodes[0].username)"

    local redis_port="$(extract_port "$(get_config .atomdb.redis.endpoint)")"
    local redis_user="$(get_config .atomdb.redis.nodes[0].username)"

    das-cli db start

    run das-cli db start

    assert_output --partial "Redis is already running"
    assert_output --partial "${redis_port}"
    assert_output --partial "${redis_user}"

    assert_output --partial "MongoDB is already running"
    assert_output --partial "${mongodb_port}"
    assert_output --partial "${mongodb_user}"

    run is_service_up das-cli-redis-40020
    assert_success

    run is_service_up das-cli-mongodb-40021
    assert_success
}

@test "It should restart even though services are stopped" {
    local mongodb_port="$(extract_port "$(get_config .atomdb.mongodb.endpoint)")"
    local mongodb_user="$(get_config .atomdb.mongodb.nodes[0].username)"

    local redis_port="$(extract_port "$(get_config .atomdb.redis.endpoint)")"
    local redis_user="$(get_config .atomdb.redis.nodes[0].username)"

    run das-cli db restart

    assert_output --partial "already stopped"
    assert_output --partial "Redis has started successfully"
    assert_output --partial "MongoDB has started successfully"

    run is_service_up das-cli-redis-40020
    assert_success

    run is_service_up das-cli-mongodb-40021
    assert_success
}

@test "It should restart db successfully when db is already up" {
    local mongodb_user="$(get_config .atomdb.mongodb.nodes[0].username)"
    local redis_user="$(get_config .atomdb.redis.nodes[0].username)"

    das-cli db start

    run das-cli db restart

    assert_output --partial "has been stopped"
    assert_output --partial "${redis_user}"
    assert_output --partial "${mongodb_user}"

    assert_output --partial "has started successfully"

    run is_service_up das-cli-redis-40020
    assert_success

    run is_service_up das-cli-mongodb-40021
    assert_success
}

@test "It should restart db and prune its volumes" {
    das-cli db start

    local mongodb_volumes="$(get_service_volumes "mongodb")"
    local redis_volumes="$(get_service_volumes "redis")"

    run das-cli db restart --prune

    assert_output --partial "has started successfully"

    run is_service_up das-cli-redis-40020
    assert_success

    run is_service_up das-cli-mongodb-40021
    assert_success

    run all_volumes_exist "${mongodb_volumes[@]}"
    assert_failure

    run all_volumes_exist "${redis_volumes[@]}"
    assert_failure
}

@test "It should stop db successfully" {
    local mongodb_user="$(get_config .atomdb.mongodb.nodes[0].username)"
    local redis_user="$(get_config .atomdb.redis.nodes[0].username)"

    das-cli db start &>/dev/null

    run das-cli db stop

    assert_output --partial "has been stopped"
    assert_output --partial "${redis_user}"
    assert_output --partial "${mongodb_user}"

    run is_service_up das-cli-redis-40020
    assert_failure

    run is_service_up das-cli-mongodb-40021
    assert_failure
}

@test "It should stop db and prune its volume" {
    das-cli db start &>/dev/null

    local mongodb_volumes="$(get_service_volumes "mongodb")"
    local redis_volumes="$(get_service_volumes "redis")"

    run das-cli db stop --prune

    assert_output --partial "has been stopped"

    run is_service_up das-cli-redis-40020
    assert_failure

    run is_service_up das-cli-mongodb-40021
    assert_failure

    run all_volumes_exist "${mongodb_volumes[@]}"
    assert_failure

    run all_volumes_exist "${redis_volumes[@]}"
    assert_failure
}

@test "It should warns up when db is already stopped" {
    run das-cli db stop

    assert_output --partial "already stopped"

    run is_service_up das-cli-redis-40020
    assert_failure

    run is_service_up das-cli-mongodb-40021
    assert_failure
}

@test "Should count atoms" {
    das-cli db restart &>/dev/null

    das-cli metta load "$test_fixtures_dir/metta/animals.metta" &>/dev/null

    run das-cli db count-atoms

    assert_success
    assert_regex "$output" '(MongoDB\s.*:\s[0-9]+)'
}

@test "Should count atoms with empty database" {
    das-cli db restart &>/dev/null

    run das-cli db count-atoms

    assert_success
    assert_output --partial "No collections found"
}

@test "Should count atoms with database disabled" {
    local redis_container_name="das-cli-redis-40020"
    local redis_port="$(get_config .services.redis.port)"
    local mongodb_container_name="das-cli-mongodb-40021"
    local mongodb_port="$(get_config .services.mongodb.port)"

    run das-cli db count-atoms

    assert_success
    assert_output --partial "$DOCKER_CONTAINER_MISSING"
    assert_output --partial "Please use 'db start'"
}