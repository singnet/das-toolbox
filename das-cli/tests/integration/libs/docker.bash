#!/bin/bash

openfaas_repository="trueagi/openfaas"

function run_authorization_admin() {
    local image="$1"
    local config_file="$2"
    shift 2

    [[ -f "$config_file" ]] || {
        echo "Authorization config file not found: $config_file" >&2
        return 1
    }

    timeout 60 docker run --rm --pull never \
        --name das-cli-authorization-admin \
        --network host \
        --user "$(id -u):$(id -g)" \
        --mount "type=bind,src=$config_file,dst=/tmp/authorization-config.json,readonly" \
        --entrypoint authorization_admin \
        "$image" "$@" --config /tmp/authorization-config.json </dev/null
}

function stop_simple_stack() {
    local prune=false
    local cleanup_status=0
    local container volume container_volumes
    local volumes=()
    local services=(command-router query-agent attention-broker db)
    local database_containers=(das-cli-redis-40020 das-cli-mongodb-40021)
    local containers=(
        das-cli-authorization-admin
        das-command-router-40008
        das-query-engine-40002
        das-attention-broker-40001
        "${database_containers[@]}"
    )

    case "${1:-}" in
        '') ;;
        --prune) prune=true ;;
        *) echo 'Usage: stop_simple_stack [--prune]' >&2; return 2 ;;
    esac
    if (( $# > 1 )); then
        echo 'Usage: stop_simple_stack [--prune]' >&2
        return 2
    fi

    if [[ "$prune" == true ]]; then
        docker info >/dev/null || return 1
        for container in "${database_containers[@]}"; do
            if docker container inspect "$container" >/dev/null 2>&1; then
                container_volumes="$(get_container_volumes "$container")" || return 1
                while IFS= read -r volume; do
                    [[ -z "$volume" ]] || volumes+=("$volume")
                done <<<"$container_volumes"
            fi
        done
    fi

    local service
    for service in "${services[@]}"; do
        das-cli "$service" stop >/dev/null 2>&1 || true
    done

    for container in "${containers[@]}"; do
        if [[ "$prune" == true ]]; then
            if docker container inspect "$container" >/dev/null 2>&1; then
                docker container rm -f "$container" >/dev/null || cleanup_status=1
            fi
        else
            docker rm -f "$container" >/dev/null 2>&1 || true
        fi
    done

    for volume in "${volumes[@]}"; do
        if volume_exists "$volume"; then
            docker volume rm "$volume" >/dev/null || cleanup_status=1
        fi
    done
    return "$cleanup_status"
}

function is_container_running() {
    local container_name="$1"
    if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}\$"; then
        return 1
    fi

    return 0
}


function is_service_up() {
    local container_name

    container_name="$1"

    is_container_running "$container_name"

    return $?
}

function service_stop() {
    local container_name
    local service_name="$1"

    container_name=$(get_config ".services.${service_name}.container_name")

    docker container rm -f "$container_name" &>/dev/null
}

function services_stop() {
    services="$(docker ps | grep das-cli | cut -d" " -f 1)"

    if [ -z "$services" ]; then
        return
    fi

    echo "$services" | xargs docker rm -f
}

function exec_cmd_on_service() {
    local container_name
    local service_name="$1"
    local cmd="$2"

    if ! is_service_up "$service_name"; then
        return 1
    fi

    container_name=$(get_config ".services.${service_name}.container_name")

    docker container exec -it "$container_name" sh -c "$cmd"

    return 0
}

function set_ssh_context() {
    local context_name
    local context_username="$1"
    local context_ip="$2"

    context_name="$(
        tr -dc A-Za-z0-9 </dev/urandom | head -c 13
        echo
    )"

    docker context create --description "This context is managed by das-cli (integration-test)" --docker="host=ssh://$context_username@$context_ip" "$context_name" &>/dev/null

    echo "$context_name"
}

function unset_ssh_context() {
    local context_name="$1"

    if docker context inspect "$context_name" &>/dev/null; then
        docker context rm "$context_name" &>/dev/null
    fi
}

function get_disgest_local_image() {
    local image="$1"
    local digest=""

    digest="$(docker image inspect $image | jq -r '.[].RepoDigests[0]' | sed 's/.*@//')"

    echo "${digest}"
}

function is_digest_same_as_remote_faas_latest_function() {
    local digest="$1"
    local url="https://hub.docker.com/v2/repositories/trueagi/openfaas/tags?page_size=1&page=1&ordering=&name=query-engine-latest"

    latest_digest=$(curl -s "$url" | jq -r '.results[0].images[0].digest')

    if [ "${digest}" = "${latest_digest}" ]; then
        return 0
    fi

    return 1
}

function get_latest_image_tag() {
    local repository="$1"
    local filter="$2"
    local url="https://registry.hub.docker.com/v2/repositories/${repository}/tags"
    local response
    local all_tags
    local filtered_tags
    local latest_version

    response=$(curl -s "${url}?page_size=100")

    if [ -z "${response}" ]; then
        echo "Error: Failed to fetch tags from Docker registry."
        return 1
    fi

    all_tags=$(echo "${response}" | jq -r '.results[].name')

    filtered_tags=$(echo "${all_tags}" | grep "${filter}")

    if [ -z "${filtered_tags}" ]; then
        echo "Error: No tags matching the filter '${filter}' found."
        return 1
    fi

    latest_version=$(echo "${filtered_tags}" | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -n 1)

    if [ -z "${latest_version}" ]; then
        echo "Error: Failed to determine the latest version."
        return 1
    fi

    echo "${latest_version}"
}

function resolve_openfaas_version() {
    local version="$1"

    if [ "$version" == "latest" ]; then
        version="latest ($(get_latest_image_tag $openfaas_repository))"
    fi

    echo "$version"
}

function get_service_volumes() {
    local service_name="$1"
    local container_name

    container_name=$(get_config ".services.${service_name}.container_name")

    if [[ -z "$container_name" ]]; then
        echo "Container name not found for service: $service_name" >&2
        return 1
    fi

    get_container_volumes "$container_name"
}

function get_container_volumes() {
    local container_name="$1"
    local container_info

    container_info="$(docker container inspect "$container_name")" || return 1
    printf '%s\n' "$container_info" \
        | jq -r '.[0].Mounts[] | select(.Type=="volume") | .Name'
}

function volume_exists() {
    local volume_id="$1"

    if docker volume inspect "$volume_id" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

function all_volumes_exist() {
    local volumes=("$@")

    for vol in "${volumes[@]}"; do
        if ! volume_exists "$vol"; then
            return 1
        fi
    done

    return 0
}

function get_docker_gateway() {
    local container_id="$1"
    
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}' "$container_id"
}
