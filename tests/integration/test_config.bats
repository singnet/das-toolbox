#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"
}

@test "listing config with unset configuration file" {
    unset_config

    run das-cli config list

    assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "listing config with set configuration file" {
    run das-cli config list

    assert_line --partial "$(get_config ".redis.port")"
    assert_line --partial "$(get_config ".redis.container_name")"
    assert_line --partial $(capitalize_letter --first "$(get_config ".redis.cluster")")
    assert_line --partial "$(get_config ".redis.nodes.0.context")"
    assert_line --partial "$(get_config ".redis.nodes.0.ip")"
    assert_line --partial "$(get_config ".redis.nodes.0.username")"
    assert_line --partial "$(get_config ".mongodb.port")"
    assert_line --partial "$(get_config ".mongodb.container_name")"
    assert_line --partial "$(get_config ".mongodb.username")"
    assert_line --partial "$(get_config ".mongodb.password")"
    assert_line --partial "$(get_config ".loader.container_name")"
    assert_line --partial "$(get_config ".openfaas.container_name")"
    assert_line --partial "$(get_config ".openfaas.version")"
    assert_line --partial "$(get_config ".openfaas.function")"
    assert_line --partial "$(get_config ".jupyter_notebook.port")"
    assert_line --partial "$(get_config ".jupyter_notebook.container_name")"

}

@test "configuring settings without a previously set configuration file" {
    unset_config

    ! [ -f "$das_config_file" ]

    local redis_port="6379"
    local redis_cluster="no"
    local mongodb_port="27017"
    local mongodb_username="admin"
    local mongodb_password="admin"
    local mongodb_cluster="no"
    local jupyter_notebook_port="8888"

    run das-cli config set <<EOF
$redis_port
$redis_cluster
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$jupyter_notebook_port
EOF

    assert_equal "$(get_config ".redis.port")" "$redis_port"
    assert_equal "$(get_config ".redis.cluster")" "$(human_to_boolean "$redis_cluster")"
    assert_equal "$(get_config ".redis.nodes | length")" 1
    assert_equal "$(get_config ".mongodb.port")" "$mongodb_port"
    assert_equal "$(get_config ".mongodb.username")" "$mongodb_username"
    assert_equal "$(get_config ".mongodb.password")" "$mongodb_password"
    assert_equal "$(get_config ".mongodb.cluster")" "$(human_to_boolean "$mongodb_cluster")"
    assert_equal "$(get_config ".jupyter_notebook.port")" "$jupyter_notebook_port"
}

@test "configuring settings with a previously set configuration file" {
    [ -f "$das_config_file" ]

    local old_redis_port="$(get_config ".redis.port")"
    local old_redis_cluster="$(get_config ".redis.cluster")"
    local old_mongodb_port="$(get_config ".mongodb.port")"
    local old_mongodb_username="$(get_config ".mongodb.username")"
    local old_mongodb_password="$(get_config ".mongodb.password")"
    local old_mongodb_cluster="$(get_config ".mongodb.cluster")"
    local old_jupyter_notebook_port="$(get_config ".jupyter_notebook.port")"

    local redis_port="7000"
    local redis_cluster="no"
    local mongodb_port="91032"
    local mongodb_username=""
    local mongodb_password="new_password"
    local mongodb_cluster="no"
    local jupyter_notebook_port="8000"

    run das-cli config set <<EOF
$redis_port
$redis_cluster
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$jupyter_notebook_port
EOF

    assert_equal "$(get_config ".redis.port")" "$redis_port"
    assert_equal "$(get_config ".redis.cluster")" "$(human_to_boolean "$redis_cluster")"
    assert_equal "$(get_config ".redis.nodes | length")" 1
    assert_equal "$(get_config ".mongodb.port")" "$mongodb_port"
    assert_not_equal "$(get_config ".mongodb.username")" "$mongodb_username"
    assert_equal "$(get_config ".mongodb.password")" "$mongodb_password"
    assert_equal "$(get_config ".mongodb.cluster")" "$(human_to_boolean "$mongodb_cluster")"
    assert_equal "$(get_config ".jupyter_notebook.port")" "$jupyter_notebook_port"

    assert_not_equal "$redis_port" "$old_redis_port"
    assert_equal "$(human_to_boolean "$redis_cluster")" "$old_redis_cluster"
    assert_not_equal "$mongodb_port" "$old_mongodb_port"
    assert_equal "$(get_config ".mongodb.username")" "$old_mongodb_username"
    assert_not_equal "$mongodb_password" "$old_mongodb_password"
    assert_equal "$(human_to_boolean "$mongodb_cluster")" "$old_mongodb_cluster"
    assert_not_equal "$jupyter_notebook_port" "$old_jupyter_notebook_port"

}

@test "setting default values for configuration" {
    [ -f "$das_config_file" ]

    local old_redis_port="$(get_config ".redis.port")"
    local old_redis_cluster="$(get_config ".redis.cluster")"
    local old_mongodb_port="$(get_config ".mongodb.port")"
    local old_mongodb_username="$(get_config ".mongodb.username")"
    local old_mongodb_password="$(get_config ".mongodb.password")"
    local old_mongodb_cluster="$(get_config ".mongodb.cluster")"
    local old_jupyter_notebook_port="$(get_config ".jupyter_notebook.port")"

    local redis_port=""
    local redis_cluster=""
    local mongodb_port=""
    local mongodb_username=""
    local mongodb_password=""
    local mongodb_cluster=""
    local jupyter_notebook_port=""

    run das-cli config set <<EOF
$redis_port
$redis_cluster
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$jupyter_notebook_port
EOF

    assert_not_equal "$(get_config ".redis.port")" "$redis_port"
    assert_not_equal "$(get_config ".redis.cluster")" "$(human_to_boolean "$redis_cluster")"
    assert_not_equal "$(get_config ".mongodb.port")" "$mongodb_port"
    assert_not_equal "$(get_config ".mongodb.username")" "$mongodb_username"
    assert_not_equal "$(get_config ".mongodb.password")" "$mongodb_password"
    assert_not_equal "$(get_config ".mongodb.cluster")" "$(human_to_boolean "$mongodb_cluster")"
    assert_not_equal "$(get_config ".jupyter_notebook.port")" "$jupyter_notebook_port"

    assert_equal "$old_redis_port" "$(get_config ".redis.port")"
    assert_equal "$old_redis_cluster" "$(get_config ".redis.cluster")"
    assert_equal "$old_mongodb_port" "$(get_config ".mongodb.port")"
    assert_equal "$old_mongodb_username" "$(get_config ".mongodb.username")"
    assert_equal "$old_mongodb_password" "$(get_config ".mongodb.password")"
    assert_equal "$old_mongodb_cluster" "$(get_config ".mongodb.cluster")"
    assert_equal "$old_jupyter_notebook_port" "$(get_config ".jupyter_notebook.port")"
}
