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

function gkctl_join_and_reserve_ports_range() {
    local range_arg="${1:-}"
    local join_cmd="gkctl instance join"
    local reserve_cmd="gkctl port reserve"

    if [[ "$range_arg" =~ ^--range=([0-9]+)$ ]]; then
        local port_range_size="${BASH_REMATCH[1]}"
        reserve_cmd="gkctl port reserve --range=${port_range_size}"
    fi

    if ! gkctl instance list --current >/dev/null 2>&1; then
        eval "$join_cmd" || {
            return 1
        }
    fi

    eval "$reserve_cmd"
}

function gkctl_release_ports_range() {
    local range_arg="${1:-}"
    local release_cmd="gkctl port release"

    if [[ "$range_arg" =~ ^--range=([0-9]+:[0-9]+)$ ]]; then
        local port_range="${BASH_REMATCH[1]}"
        release_cmd="gkctl port release --range=${port_range}"
    fi

    if gkctl instance list --current >/dev/null 2>&1; then
        if ! eval "$release_cmd" >/dev/null 2>&1; then
            return 1
        fi
    fi

    return 0
}


function get_port_range() {
    local fallback_range="12000:13000"

    if command -v gkctl >/dev/null 2>&1; then
        local reserved_port
        reserved_port=$(gkctl_join_and_reserve_ports_range --range=1000 | tail -n 1)

        if [[ -n "$reserved_port" ]]; then
            echo "$reserved_port"
            return 0
        fi
    fi

    echo "$fallback_range"
}

function release_port_range() {
   local port_range="${1:-}"

    if [[ -z "$port_range" ]]; then
        echo "[ERROR] No port range specified. Usage: release_port_range START:END"
        return 1
    fi

    if command -v gkctl >/dev/null 2>&1; then
        if ! gkctl port release --range="$port_range" >/dev/null 2>&1; then
            echo "[ERROR] Failed to release port range: $port_range"
            return 1
        fi
    fi

    echo $port_range
}
