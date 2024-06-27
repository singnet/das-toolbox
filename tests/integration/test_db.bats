#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"

    das-cli faas stop
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
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_port="$(get_config .redis.port)"

    run das-cli db start

    assert_output <<EOF
Starting redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the user ${CURRENT_USER}.
Starting mongodb service...
MongoDB started on port ${mongodb_port}
EOF

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should gives up a warning when db is already up" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_port="$(get_config .redis.port)"

    das-cli db start

    run das-cli db start

    assert_output <<EOF
Starting redis service...
Redis is already running. It is currently listening on port ${redis_port} at IP address localhost under the user ${current_user}.
Starting mongodb service...
MongoDB is already running. It's listening on port ${mongodb_port}
EOF

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should restart even though services are stopped" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_port="$(get_config .redis.port)"
    local redis_container_name="$(get_config .redis.container_name)"
    local mongodb_container_name="$(get_config .mongodb.container_name)"

    run das-cli db restart

    assert_output <<EOF
Stopping redis service...
The Redis service named ${redis_container_name} at localhost is already stopped by the ${current_user} user.
The MongoDB service named ${mongodb_container_name} is already stopped.
Starting redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the user ${current_user}.
Starting mongodb service...
MongoDB started on port ${mongodb_port}
EOF

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should restart db successfully when db is already up" {
    local mongodb_port="$(get_config ".mongodb.port")"
    local redis_port="$(get_config .redis.port)"

    das-cli db start

    run das-cli db restart

    assert_output <<EOF
Stopping redis service...
The Redis service at localhost has been stopped by the ${current_user} user
MongoDB service stopped
Starting redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the user ${current_user}.
Starting mongodb service...
MongoDB started on port ${mongodb_port}
EOF

    run is_service_up redis
    assert_success

    run is_service_up mongodb
    assert_success
}

@test "It should stop db successfully" {
    das-cli db start &>/dev/null

    run das-cli db stop

    assert_output <<EOF
Stopping redis service...
The Redis service at localhost has been stopped by the ${current_user} user
MongoDB service stopped
EOF

    run is_service_up redis
    assert_failure

    run is_service_up mongodb
    assert_failure
}

@test "It should warns up when db is already stopped" {
    local redis_container_name="$(get_config .redis.container_name)"
    local mongodb_container_name="$(get_config .mongodb.container_name)"

    run das-cli db stop

    assert_output <<EOF
Stopping redis service...
The Redis service named ${redis_container_name} at localhost is already stopped by the ${current_user} user.
The MongoDB service named ${mongodb_container_name} is already stopped.
EOF

    run is_service_up redis
    assert_failure

    run is_service_up mongodb
    assert_failure
}

# bats test_tags=redis:cluster
@test "Starting db with redis cluster" {
    set_config ".redis.cluster" true
    set_config ".redis.nodes" "[
    {
        "context": "default",
        "ip": "localhost",
        "username": "$current_user"
    },
    {
        "context": "default",
        "ip": "172.17.0.6",
        "username": "root"
    },
    {
        "context": "default",
        "ip": "172.17.0.5",
        "username": "root"
    }
]"

    run das-cli db start

        assert_output <<EOF
Starting redis service...
Redis has started successfully on port ${redis_port} at localhost, operating under the user ${CURRENT_USER}.
Starting mongodb service...
MongoDB started on port ${mongodb_port}
EOF

    assert_success
}
