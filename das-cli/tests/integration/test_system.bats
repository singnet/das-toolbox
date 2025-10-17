#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    for service in db attention-broker query-agent; do
        das-cli "$service" stop
    done
}

wait_for_service() {
    local service=$1
    local timeout=${2:-30}
    local interval=1

    local elapsed=0
    until is_service_up "$service"; do
        sleep $interval
        elapsed=$((elapsed + interval))
        if [ $elapsed -ge $timeout ]; then
            return 1
        fi
    done
    return 0
}

wait_for_service_down() {
    local service=$1
    local timeout=${2:-30}
    local interval=1

    local elapsed=0
    until ! is_service_up "$service"; do
        sleep $interval
        elapsed=$((elapsed + interval))
        if [ $elapsed -ge $timeout ]; then
            return 1
        fi
    done
    return 0
}

@test "Trying to show the system status with unset configuration file" {
    unset_config

    run das-cli system status

    assert_output --partial "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "Show system status" {
    run das-cli system status

    for header in NAME VERSION STATUS PORT "PORT RANGE"; do
        assert_line --partial "$header"
    done

    for service in db attention-broker query-agent; do
        das-cli "$service" start
        wait_for_service "$service"
    done

    for service in redis mongodb attention-broker query-agent; do
        wait_for_service "$service"
        run is_service_up "$service"
        assert_success
    done

    count_services_up=$(echo "$output" | awk '$3=="running" {print $1}' | wc -l)
    assert [ "$count_services_up" -eq 4 ]

    for service in db attention-broker query-agent; do
        das-cli "$service" stop
        wait_for_service_down "$service"
    done

    for service in redis mongodb attention-broker query-agent; do
        wait_for_service_down "$service"
        run is_service_up "$service"
        assert_failure
    done

    run das-cli system status
    count_services_up=$(echo "$output" | awk '$3=="running" {print $1}' | wc -l)
    assert [ "$count_services_up" -eq 0 ]
}
