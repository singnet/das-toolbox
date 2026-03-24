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

    assert_line --partial "$(get_config ".atomdb.redis.endpoint")"
    assert_line --partial $(capitalize_letter --first "$(get_config ".atomdb.redis.cluster")")
    assert_line --partial "$(get_config ".atomdb.mongodb.endpoint")"
    assert_line --partial "$(get_config ".atomdb.mongodb.username")"
    assert_line --partial "$(get_config ".atomdb.mongodb.password")"
    assert_line --partial "$(get_config ".environment.jupyter.endpoint")"
    assert_line --partial "$(get_config ".brokers.attention.endpoint")"
    assert_line --partial "$(get_config ".agents.query.endpoint")"
    assert_line --partial "$(get_config ".agents.link_creation.endpoint")"
    assert_line --partial "$(get_config ".agents.inference.endpoint")"
    assert_line --partial "$(get_config ".agents.evolution.endpoint")"
    assert_line --partial "$(get_config ".brokers.context.endpoint")"
    assert_line --partial "$(get_config ".atomdb.type")"
}

@test "configuring settings without a previously set configuration file" {
    local atomdb_backend="" 
    local mongodb_port="40021"
    local mongodb_username="admin"
    local mongodb_password="admin"
    local mongodb_cluster="" 
    local redis_port="40020"
    local redis_cluster=""  
    
    local query_agent_port="40002"
    local query_agent_range="42000:42999"
    local link_creation_agent_port="40003"
    local link_creation_agent_range="43000:43999"
    local inference_agent_port="40004"
    local inference_agent_range="44000:44999"
    local evolution_agent_port="40005"
    local evolution_agent_range="45000:45999"
    
    local attention_broker_port="40001"
    local context_broker_port="40006"
    local context_broker_range="46000:46999"
    local atomdb_broker_port="40007"
    local atomdb_broker_range="47000:47999"
    
    local jupyter_notebook_port="40017"
    local custom_params="" 

run das-cli config set <<EOF
$atomdb_backend
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$redis_port
$redis_cluster
$query_agent_port
$query_agent_range
$link_creation_agent_port
$link_creation_agent_range
$inference_agent_port
$inference_agent_range
$evolution_agent_port
$evolution_agent_range
$attention_broker_port
$context_broker_port
$context_broker_range
$atomdb_broker_port
$atomdb_broker_range
$jupyter_notebook_port
$custom_params
EOF

    assert_success
    
    run get_config ".atomdb.redis.endpoint"
    assert_output "localhost:40020"

    run get_config ".atomdb.mongodb.endpoint"
    assert_output "localhost:40021"

    run get_config ".environment.jupyter.endpoint"
    assert_output "localhost:40017"
}

@test "configuring settings with a previously set configuration file" {
    unset_config

    local atomdb_backend=""
    local mongodb_port="40021"
    local mongodb_username="admin"
    local mongodb_password="admin"
    local mongodb_cluster="n"
    local redis_port="40020"
    local redis_cluster="n"

    local query_agent_port="40002"
    local query_agent_range="42000:42999"
    local link_creation_agent_port="40003"
    local link_creation_agent_range="43000:43999"
    local inference_agent_port="40004"
    local inference_agent_range="44000:44999"
    local evolution_agent_port="40005"
    local evolution_agent_range="45000:45999"

    local attention_broker_port="40001"
    local context_broker_port="40006"
    local context_broker_range="46000:46999"
    local atomdb_broker_port="40007"
    local atomdb_broker_range="47000:47999"

    local jupyter_notebook_port="40017"
    local custom_params="n"

    run das-cli config set <<EOF
$atomdb_backend
$mongodb_port
$mongodb_username
$mongodb_password
$mongodb_cluster
$redis_port
$redis_cluster
$query_agent_port
$query_agent_range
$link_creation_agent_port
$link_creation_agent_range
$inference_agent_port
$inference_agent_range
$evolution_agent_port
$evolution_agent_range
$attention_broker_port
$context_broker_port
$context_broker_range
$atomdb_broker_port
$atomdb_broker_range
$jupyter_notebook_port
$custom_params
EOF

    assert_success

    assert_equal "$(get_config ".atomdb.redis.endpoint")" "localhost:$redis_port"
    assert_equal "$(get_config ".atomdb.mongodb.endpoint")" "localhost:$mongodb_port"
    assert_equal "$(get_config ".environment.jupyter.endpoint")" "localhost:$jupyter_notebook_port"

    assert_equal "$(get_config ".agents.query.endpoint")" "localhost:$query_agent_port"
    assert_equal "$(get_config ".agents.query.ports_range")" "$query_agent_range"

    assert_equal "$(get_config ".agents.link_creation.endpoint")" "localhost:$link_creation_agent_port"
    assert_equal "$(get_config ".agents.link_creation.ports_range")" "$link_creation_agent_range"

    assert_equal "$(get_config ".agents.inference.endpoint")" "localhost:$inference_agent_port"
    assert_equal "$(get_config ".agents.inference.ports_range")" "$inference_agent_range"

    assert_equal "$(get_config ".agents.evolution.endpoint")" "localhost:$evolution_agent_port"
    assert_equal "$(get_config ".agents.evolution.ports_range")" "$evolution_agent_range"

    assert_equal "$(get_config ".brokers.attention.endpoint")" "localhost:$attention_broker_port"

    assert_equal "$(get_config ".brokers.context.endpoint")" "localhost:$context_broker_port"
    assert_equal "$(get_config ".brokers.context.ports_range")" "$context_broker_range"

    assert_equal "$(get_config ".brokers.atomdb.endpoint")" "localhost:$atomdb_broker_port"
    assert_equal "$(get_config ".brokers.atomdb.ports_range")" "$atomdb_broker_range"
}


@test "Raises error value when configuration schema version does not match" {
    [ -f "$das_config_file" ]

    local old_shema_hash="$(get_config ".schema_version")"
    local current_schema_hash="2.0"

    update_json_key "$das_config_file" schema_version "$current_schema_hash"

    assert_not_equal "$old_schema_hash" "$current_schema_hash"

    run das-cli config list

    assert_output "[31m[ValueError] Your configuration file in ${das_config_file} doesn't have all the entries this version of das-cli requires. You can call 'das-cli config set' and hit <ENTER> to every prompt in order to re-use the configuration you currently have in your config file and set the new ones to safe default values.[39m"
}
