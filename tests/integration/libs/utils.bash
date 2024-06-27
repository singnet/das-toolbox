#!/bin/bash

current_user="$(whoami)"

export current_user
export test_fixtures_dir="${BATS_TEST_DIRNAME}/fixtures"
export das_log_file="/tmp/$current_user-das-cli.log"
export das_config_dir="${HOME}/.das"
export das_config_file="${das_config_dir}/config.json"

function get_das_cli_latest_version() {
    local package_name="$1"

    apt-cache showpkg "$package_name" | grep 'Versions:' -A1 | tail -n 1 | awk '{print $1}'
}

function get_das_cli_version() {
    das-cli --version | grep -oP '(?<=das-cli )[\d.]+'
}

function get_python_package_version() {
    local package_name=$1
    local version

    version=$(pip show "$package_name" 2>/dev/null | grep '^Version:' | awk '{print $2}')

    if [ -z "$version" ]; then
        echo "Package not found"
    else
        echo "$version"
    fi
}

function get_python_package_latest_version() {
    local package=$1
    local url="https://pypi.org/pypi/$package/json"
    local latest_version

    latest_version=$(curl -s "$url" | jq -r '.info.version')

    if [ -z "$latest_version" ]; then
        echo "unknown"
        return 1
    fi

    echo "$latest_version"
    return 0
}

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

function human_to_boolean() {
    local response="${1,,}"

    case "$response" in
    y | yes)
        echo "true"
        return 0
        ;;
    n | no)
        echo "false"
        return 1
        ;;
    esac
}

function capitalize_letter() {
    local option="$1"
    local string="$2"
    local result=""

    case "$option" in
    --first)
        result="${string^}"
        ;;
    --all)
        local words=("$string")
        local capitalized=("${words[@]^}")
        result="${capitalized[*]}"
        ;;
    *)
        echo "Invalid option. Usage: capitalize_letter [--first|--all] <string>"
        return 1
        ;;
    esac

    echo "$result"
}

function get_config() {
    local attr="$1"

    jq -r -c ''"${attr}"'' "$das_config_file"
}

function set_config() {
    local attr="$1"
    local value="$2"

    jq "$attr = $value" "$das_config_file" >"$das_config_file.tmp" &&
        mv "$das_config_file.tmp" "$das_config_file"
}

function unset_config() {
    if [ -f "$das_config_file" ]; then
        rm "$das_config_file"
    fi
}

function unset_log() {
    if [ -f "$das_log_file" ]; then
        rm "$das_log_file"
    fi
}

function use_config() {
    local config="$1"
    local config_path="${test_fixtures_dir}/config/${config}.json"

    [ -f "${config_path}" ] || {
        echo "Config '${config_path}' do not exist" && exit 1
    }

    mkdir -p "${das_config_dir}"

    unset_config

    cp "${config_path}" "${das_config_file}"
}
