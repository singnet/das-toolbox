#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db start
    das-cli faas stop
}

teardown() {
    das-cli db stop
}

@test "Start FaaS when port is already in use" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local faas_port=8080


    run listen_port "${faas_port}"
    assert_success

    run das-cli faas start
    assert_output "MongoDB is running on port ${mongodb_port}
Redis is running on port ${redis_port}
Starting OpenFaaS...
[31m[DockerError] Port ${faas_port} is already in use. Please stop the service that is currently using this port.[39m"

    run stop_listen_port "${faas_port}"
    assert_success

    run is_service_up openfaas
    assert_failure
}

@test "Start FaaS when metric port is already in use" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local metric_port=8081

    run listen_port "${metric_port}"
    assert_success

    run das-cli faas start
    assert_output "MongoDB is running on port ${mongodb_port}
Redis is running on port ${redis_port}
Starting OpenFaaS...
[31m[DockerError] Port ${metric_port} is already in use. Please stop the service that is currently using this port.[39m"

    run stop_listen_port "${metric_port}"
    assert_success

    run is_service_up openfaas
    assert_failure
}

@test "Start FaaS when datadog port is already in use" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local datadog_port=5000

    run listen_port "${datadog_port}"
    assert_success

    run das-cli faas start
    assert_output "MongoDB is running on port ${mongodb_port}
Redis is running on port ${redis_port}
Starting OpenFaaS...
[31m[DockerError] Port ${datadog_port} is already in use. Please stop the service that is currently using this port.[39m"

    run stop_listen_port "${datadog_port}"
    assert_success

    run is_service_up openfaas
    assert_failure
}

@test "Trying to start, stop and restart the FaaS with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli db $cmd

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Starting the FaaS with both redis and mongodb down" {
    das-cli db stop

    run das-cli faas start

    assert_output "MongoDB is not running
Redis is not running
[31m[DockerContainerNotFoundError] 
Please use 'db start' to start required services before running 'faas start'.[39m"

    run is_service_up openfaas

    assert_failure
}

@test "Starting the FaaS with redis up-and-running and mongodb down" {
    service_stop "mongodb"

    run das-cli faas start

    local redis_port="$(get_config ".redis.port")"

    assert_output "MongoDB is not running
Redis is running on port $redis_port
[31m[DockerContainerNotFoundError] 
Please use 'db start' to start required services before running 'faas start'.[39m"

    run is_service_up openfaas

    assert_failure
}

@test "Starting the FaaS with mongodb up-and-running and redis down" {
    service_stop "redis"

    run das-cli faas start

    local mongodb_port="$(get_config ".mongodb.port")"

    assert_output "MongoDB is running on port $mongodb_port
Redis is not running
[31m[DockerContainerNotFoundError] 
Please use 'db start' to start required services before running 'faas start'.[39m"

    run is_service_up openfaas

    assert_failure
}

@test "Starting the FaaS function" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local openfaas_version="$(get_config .openfaas.version)"
    local openfaas_resolved_version="$(resolve_openfaas_version $openfaas_version)"

    run das-cli faas start

    assert_output "MongoDB is running on port $mongodb_port
Redis is running on port $redis_port
Starting OpenFaaS...
You are running the version '$openfaas_resolved_version' of the function.
OpenFaaS running on port 8080"

    run is_service_up openfaas

    assert_success
}

@test "Starting the FaaS function when function is already up" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local openfaas_version="$(get_config .openfaas.version)"
    local openfaas_resolved_version="$(resolve_openfaas_version $openfaas_version)"

    das-cli faas start

    run das-cli faas start

    assert_output "MongoDB is running on port $mongodb_port
Redis is running on port $redis_port
Starting OpenFaaS...
You are running the version '$openfaas_resolved_version' of the function.
OpenFaaS running on port 8080"

    run is_service_up openfaas

    assert_success
}

@test "Stopping the FaaS function after it has started and is running" {
    das-cli faas start

    run das-cli faas stop

    assert_output "Stopping OpenFaaS service...
OpenFaaS service stopped"

    run is_service_up openfaas

    assert_failure
}

@test "Stopping the FaaS function before it has started" {
    run das-cli faas stop

    assert_output "Stopping OpenFaaS service...
FaaS is not running..."

    run is_service_up openfaas

    assert_failure
}

@test "Restart the FaaS function once it has been initiated" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local openfaas_version="$(get_config .openfaas.version)"
    local openfaas_resolved_version="$(resolve_openfaas_version $openfaas_version)"

    das-cli faas start

    run das-cli faas restart

    assert_output "Stopping OpenFaaS service...
OpenFaaS service stopped
MongoDB is running on port $mongodb_port
Redis is running on port $redis_port
Starting OpenFaaS...
You are running the version '$openfaas_resolved_version' of the function.
OpenFaaS running on port 8080"

    run is_service_up openfaas

    assert_success
}

@test "Restart the FaaS function even if it has not been previously initiated" {
    local mongodb_port="$(get_config .mongodb.port)"
    local redis_port="$(get_config .redis.port)"
    local openfaas_version="$(get_config .openfaas.version)"
    local openfaas_resolved_version="$(resolve_openfaas_version $openfaas_version)"

    run das-cli faas restart

    assert_output "Stopping OpenFaaS service...
FaaS is not running...
MongoDB is running on port $mongodb_port
Redis is running on port $redis_port
Starting OpenFaaS...
You are running the version '$openfaas_resolved_version' of the function.
OpenFaaS running on port 8080"

    run is_service_up openfaas

    assert_success
}

@test "Update FaaS to a non-existent version" {
    local inexistente_version="0.0.0"
    local openfaas_function="$(get_config .openfaas.function)"

    run das-cli faas update-version --version "${inexistente_version}"

    assert_output "Downloading the $openfaas_function function, version $inexistente_version...
[31m[DockerImageNotFoundError] The image trueagi/openfaas:$openfaas_function-$inexistente_version for the function could not be located in the Docker Hub repository. Please verify the existence of the version or ensure the correct function name is used.[39m"
}

@test "Update FaaS to a non-existent function" {
    local inexistenteFunction="fn"

    run das-cli faas update-version --function "${inexistenteFunction}"

    assert_failure
}

@test "Update FaaS to an existing version and existing function" {
    local new_function="query-engine"
    local new_version="1.12.0"

    local old_version="$(get_config .openfaas.version)"
    local old_function="$(get_config .openfaas.function)"

    run das-cli faas update-version --function "${new_function}" --version "${new_version}"

    assert_output "Downloading the $new_function function, version $new_version...
Function version successfully updated $old_function $old_version --> $new_function $new_version. You need to call 'faas restart' to start using the new version."

    run das-cli faas start
    assert_success

    run is_service_up openfaas
    assert_success
}

@test "Update FaaS to the latest available version" {
    local old_version="$(get_config .openfaas.version)"
    local function="$(get_config .openfaas.function)"

    run das-cli faas update-version

    assert_output "Downloading the $function function, version latest...
Function version successfully updated $function $old_version --> $function latest. You need to call 'faas restart' to start using the new version."

    local image_version_digest="$(get_disgest_local_image "$openfaas_repository:query-engine-latest")"

    run is_digest_same_as_remote_faas_latest_function "$image_version_digest" 
    assert_success

    run das-cli faas start
    assert_success

    run is_service_up openfaas
    assert_success
}

