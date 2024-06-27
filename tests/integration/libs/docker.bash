#!/bin/bash

openfaas_repository="trueagi/openfaas"

function set_ssh_context() {
    local context_name
    local context_username="$1"
    local context_ip="$2"

    context_name="$(date +%s)"

    docker context create --description "This context is managed by das-cli (integration-test)" --docker="host=ssh://$context_username@$context_ip" "$context_name" &>/dev/null

    echo "$context_name"
}

function unset_ssh_context() {
    local context_name="$1"

    if docker context inspect "$context_name" &>/dev/null; then
        docker context rm "$context_name" &>/dev/null
    fi
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
