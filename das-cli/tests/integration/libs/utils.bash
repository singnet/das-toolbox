#!/bin/bash

current_user="$(whoami)"

export current_user
export test_fixtures_dir="${BATS_TEST_DIRNAME}/fixtures"
export das_log_file="/tmp/$current_user-das-cli.log"
export das_config_dir="${HOME}/.das"
export das_config_file="${das_config_dir}/config.json"

function clean_string() {
    local a=${1//[^[:alnum:]]/}
    echo "${a,,}"
}

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

function set_log() {
    cp "$test_fixtures_dir/logs/das-cli.log" "$das_log_file"
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

function listen_port() {
    local port="$1"

    if [ ! command -v socat &>/dev/null ]; then
        echo "socat is not installed. Please install it to use this function."
        return 1
    fi

    socat TCP-LISTEN:"$port",fork,reuseaddr - >/dev/null 2>&1 &
    local pid=$!
    disown $pid

    if [ "$?" -ne 0 ]; then
        echo "It could not start listening on port $port"
        return 1
    else
        echo "Started listening on port $port with PID $pid"
    fi

}

function stop_listen_port() {
    local port="$1"
    local pids=()

    pids=($(lsof -ti :$port))

    if [ -z "$pids" ]; then
        echo "There are no service running on port $port to be stopped"
        return 1
    fi

    for pid in "${pids[@]}"; do
        kill -9 "$pid"
    done
}

function update_json_key() {
    local file="$1"
    local key_path="$2"
    local new_value="$3"

    if [[ -z "$file" || -z "$key_path" || -z "$new_value" ]]; then
        echo "Usage: update_json_key <file> <key_path> <new_value>"
        echo "Example: update_json_key config.json services.redis.port 6380"
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: File '$file' not found."
        return 1
    fi

    local jq_path=".$key_path"

    if [[ "$new_value" =~ ^[0-9]+$ ]] || [[ "$new_value" =~ ^true$|^false$ ]]; then
        jq "$jq_path = $new_value" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    else
        jq --arg val "$new_value" "$jq_path = \$val" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    fi
}
