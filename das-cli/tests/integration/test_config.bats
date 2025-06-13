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

    assert_line --partial "$(get_config .services.redis.port)"
    assert_line --partial "$(get_config .services.redis.container_name)"
    assert_line --partial "$(capitalize_letter --first $(get_config .services.redis.cluster))"
    assert_line --partial "$(get_config .services.redis.nodes.0.context)"
    assert_line --partial "$(get_config .services.redis.nodes.0.ip)"
    assert_line --partial "$(get_config .services.redis.nodes.0.username)"
    assert_line --partial "$(get_config .services.mongodb.port)"
    assert_line --partial "$(get_config .services.mongodb.container_name)"
    assert_line --partial "$(get_config .services.mongodb.username)"
    assert_line --partial "$(get_config .services.mongodb.password)"
    assert_line --partial "$(get_config .services.loader.container_name)"
    assert_line --partial "$(get_config .services.openfaas.container_name)"
    assert_line --partial "$(get_config .services.openfaas.version)"
    assert_line --partial "$(get_config .services.openfaas.function)"
    assert_line --partial "$(get_config .services.jupyter_notebook.port)"
    assert_line --partial "$(get_config .services.jupyter_notebook.container_name)"

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
    local attention_broker_port="37007"
    local query_agent_port="35700"
    local link_creation_agent_port="9080"
    local inference_agent_port="8080"

    run das-cli config set <<EOF
$redis_port
$redis_cluster
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$jupyter_notebook_port
$attention_broker_port
$query_agent_port
$link_creation_agent_port
$inference_agent_port
EOF

    assert_equal "$(get_config .services.redis.port)" "$redis_port"
    assert_equal "$(get_config .services.redis.cluster)" "$(human_to_boolean "$redis_cluster")"
    assert_equal "$(get_config .services.redis.nodes | length)" 1
    assert_equal "$(get_config .services.mongodb.port)" "$mongodb_port"
    assert_equal "$(get_config .services.mongodb.username)" "$mongodb_username"
    assert_equal "$(get_config .services.mongodb.password)" "$mongodb_password"
    assert_equal "$(get_config .services.mongodb.cluster)" "$(human_to_boolean "$mongodb_cluster")"
    assert_equal "$(get_config .services.jupyter_notebook.port)" "$jupyter_notebook_port"
    assert_equal "$(get_config .services.attention_broker.port)" "$attention_broker_port"
    assert_equal "$(get_config .services.query_agent.port)" "$query_agent_port"
    assert_equal "$(get_config .services.link_creation_agent.port)" "$link_creation_agent_port"
    assert_equal "$(get_config .services.inference_agent.port)" "$inference_agent_port"
}

@test "configuring settings with a previously set configuration file" {
    [ -f "$das_config_file" ]

    local old_redis_port="$(get_config .services.redis.port)"
    local old_redis_cluster="$(get_config .services.redis.cluster)"
    local old_mongodb_port="$(get_config .services.mongodb.port)"
    local old_mongodb_username="$(get_config .services.mongodb.username)"
    local old_mongodb_password="$(get_config .services.mongodb.password)"
    local old_mongodb_cluster="$(get_config .services.mongodb.cluster)"
    local old_jupyter_notebook_port="$(get_config .services.jupyter_notebook.port)"
    local old_attention_broker_port="$(get_config .services.attention_broker.port)"
    local old_query_agent_port="$(get_config .services.query_agent.port)"
    local old_link_creation_agent_port="$(get_config .services.link_creation_agent.port)"
    local old_inference_agent_port="$(get_config .services.inference_agent.port)"

    local redis_port="7000"
    local redis_cluster="no"
    local mongodb_port="91032"
    local mongodb_username=""
    local mongodb_password="new_password"
    local mongodb_cluster="no"
    local jupyter_notebook_port="8000"
    local attention_broker_port="38007"
    local query_agent_port="36700"
    local link_creation_agent_port="9180"
    local inference_agent_port="8080"

    run das-cli config set <<EOF
$redis_port
$redis_cluster
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$jupyter_notebook_port
$attention_broker_port
$query_agent_port
$link_creation_agent_port
$inference_agent_port
EOF

    assert_equal "$(get_config .services.redis.port)" "$redis_port"
    assert_equal "$(get_config .services.redis.cluster)" "$(human_to_boolean "$redis_cluster")"
    assert_equal "$(get_config .services.redis.nodes | length)" 1
    assert_equal "$(get_config .services.mongodb.port)" "$mongodb_port"
    assert_not_equal "$(get_config .services.mongodb.username)" "$mongodb_username"
    assert_equal "$(get_config .services.mongodb.password)" "$mongodb_password"
    assert_equal "$(get_config .services.mongodb.cluster)" "$(human_to_boolean "$mongodb_cluster")"
    assert_equal "$(get_config .services.jupyter_notebook.port)" "$jupyter_notebook_port"
    assert_equal "$(get_config .services.attention_broker.port)" "$attention_broker_port"
    assert_equal "$(get_config .services.query_agent.port)" "$query_agent_port"
    assert_equal "$(get_config .services.link_creation_agent.port)" "$link_creation_agent_port"
    assert_equal "$(get_config .services.inference_agent.port)" "$inference_agent_port"

    assert_not_equal "$redis_port" "$old_redis_port"
    assert_equal "$(human_to_boolean "$redis_cluster")" "$old_redis_cluster"
    assert_not_equal "$mongodb_port" "$old_mongodb_port"
    assert_equal "$(get_config .services.mongodb.username)" "$old_mongodb_username"
    assert_not_equal "$mongodb_password" "$old_mongodb_password"
    assert_equal "$(human_to_boolean "$mongodb_cluster")" "$old_mongodb_cluster"
    assert_not_equal "$jupyter_notebook_port" "$old_jupyter_notebook_port"
    assert_not_equal "$attention_broker_port" "$old_attention_broker_port"
    assert_not_equal "$query_agent_port" "$old_query_agent_port"
    assert_not_equal "$link_creation_agent_port" "$old_link_creation_agent_port"
    assert_not_equal "$inference_agent_port" "$old_inference_agent_port"

}

@test "setting default values for configuration" {
    [ -f "$das_config_file" ]

    local old_redis_port="$(get_config .services.redis.port)"
    local old_redis_cluster="$(get_config .services.redis.cluster)"
    local old_mongodb_port="$(get_config .services.mongodb.port)"
    local old_mongodb_username="$(get_config .services.mongodb.username)"
    local old_mongodb_password="$(get_config .services.mongodb.password)"
    local old_mongodb_cluster="$(get_config .services.mongodb.cluster)"
    local old_jupyter_notebook_port="$(get_config .services.jupyter_notebook.port)"
    local old_attention_broker_port="$(get_config .services.attention_broker.port)"
    local old_query_agent_port="$(get_config .services.query_agent.port)"
    local old_link_creation_agent_port="$(get_config .services.link_creation_agent.port)"
    local old_inference_agent_port="$(get_config .services.inference_agent.port)"

    local redis_port=""
    local redis_cluster=""
    local mongodb_port=""
    local mongodb_username=""
    local mongodb_password=""
    local mongodb_cluster=""
    local jupyter_notebook_port=""
    local attention_broker_port=""
    local query_agent_port=""
    local link_creation_agent_port=""
    local inference_agent_port=""

    run das-cli config set <<EOF
$redis_port
$redis_cluster
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$jupyter_notebook_port
$attention_broker_port
$query_agent_port
$link_creation_agent_port
$inference_agent_port
EOF

    assert_not_equal "$(get_config .services.redis.port)" "$redis_port"
    assert_not_equal "$(get_config .services.redis.cluster)" "$(human_to_boolean "$redis_cluster")"
    assert_not_equal "$(get_config .services.mongodb.port)" "$mongodb_port"
    assert_not_equal "$(get_config .services.mongodb.username)" "$mongodb_username"
    assert_not_equal "$(get_config .services.mongodb.password)" "$mongodb_password"
    assert_not_equal "$(get_config .services.mongodb.cluster)" "$(human_to_boolean "$mongodb_cluster")"
    assert_not_equal "$(get_config .services.jupyter_notebook.port)" "$jupyter_notebook_port"
    assert_not_equal "$(get_config .services.attention_broker.port)" "$attention_broker_port"
    assert_not_equal "$(get_config .services.query_agent.port)" "$query_agent_port"
    assert_not_equal "$(get_config .services.link_creation_agent.port)" "$link_creation_agent_port"
    assert_not_equal "$(get_config .services.inference_agent.port)" "$inference_agent_port"

    assert_equal "$old_redis_port" "$(get_config .services.redis.port)"
    assert_equal "$old_redis_cluster" "$(get_config .services.redis.cluster)"
    assert_equal "$old_mongodb_port" "$(get_config .services.mongodb.port)"
    assert_equal "$old_mongodb_username" "$(get_config .services.mongodb.username)"
    assert_equal "$old_mongodb_password" "$(get_config .services.mongodb.password)"
    assert_equal "$old_mongodb_cluster" "$(get_config .services.mongodb.cluster)"
    assert_equal "$old_jupyter_notebook_port" "$(get_config .services.jupyter_notebook.port)"
    assert_equal "$old_attention_broker_port" "$(get_config .services.attention_broker.port)"
    assert_equal "$old_query_agent_port" "$(get_config .services.query_agent.port)"
    assert_equal "$old_link_creation_agent_port" "$(get_config .services.link_creation_agent.port)"
    assert_equal "$old_inference_agent_port" "$(get_config .services.inference_agent.port)"
}
