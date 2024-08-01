#!/bin/bash

openfaas_repository="trueagi/openfaas"

function is_service_up() {
    local container_name
    local service_name="$1"

    container_name=$(get_config ".${service_name}.container_name")

    if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}\$"; then
        return 1
    fi

    return 0
}

function service_stop() {
    local container_name
    local service_name="$1"

    container_name=$(get_config ".${service_name}.container_name")

    docker container rm -f "$container_name" &>/dev/null
}

function exec_cmd_on_service() {
    local container_name
    local service_name="$1"
    local cmd="$2"

    if ! is_service_up "$service_name"; then
        return 1
    fi

    container_name=$(get_config ".${service_name}.container_name")

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
    local image = "$1"
    local digest = ""

    digest="$(docker inspect $image | jq '.[].RepoDigests[0]' | cut -d '@' -f 2 | sed 's/\sha256://g')"

    echo "${digest}"
}

function is_digest_same_as_remote_faas_latest_function() {
    local digest = "$1"
    local url = "https://hub.docker.com/v2/repositories/trueagi/openfaas/tags?page_size=1&page=1&ordering=&name=query-engine-latest"

    latest_digest=$(curl -s "$url" | jq -r '.results.0.digest')

    if [ "$digest" == "$latest_digest" ]; then
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
