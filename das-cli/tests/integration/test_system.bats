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

@test "Trying to show the system status with unset configuration file" {
    unset_config

    run das-cli system status

    assert_output --partial "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
}

@test "System status command correctly reports running and stopped services" { 
    for service in db attention-broker query-agent; do
        das-cli "$service" start
    done

    for service in redis mongodb attention_broker query_agent; do
        run is_service_up "$service"
        assert_success
    done

    run das-cli system status

    count_services_up=$(echo "$output" | awk '$3=="running" {print $1}' | wc -l)
    assert [ "$count_services_up" -eq 4 ]

    for header in NAME VERSION STATUS PORT "PORT RANGE"; do
        assert_line --partial "$header"
    done

    for service in db attention-broker query-agent; do
        das-cli "$service" stop
    done

    for service in redis mongodb attention_broker query_agent; do
        run is_service_up "$service"
        assert_failure
    done

    run das-cli system status
    count_services_up=$(echo "$output" | awk '$3=="running" {print $1}' | wc -l)
    assert [ "$count_services_up" -eq 0 ]
}
