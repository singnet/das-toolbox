#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    das-cli db start || true
    das-cli attention-broker start || true
    das-cli query-agent start || true
}

teardown() {
    das-cli db stop || true
    das-cli attention-broker stop || true
    das-cli query-agent stop || true
}

@test "Trying to show the system status with unset configuration file" {
    unset_config

    run das-cli system status

    assert_output --partial "$FILE_NOT_FOUND_ERROR"
}

@test "System status command correctly reports running and stopped services" { 

    services_containers=(
        "das-cli-redis-40020"
        "das-cli-mongodb-40021"
        "das-attention-broker-40001"
        "das-query-engine-40002"
    )

    # Garante que estão rodando
    for service in db attention-broker query-agent; do
        das-cli "$service" start
    done

    for container in "${services_containers[@]}"; do
        run is_service_up "$container"
        assert_success
    done

    # Verifica status com serviços rodando
    run das-cli system status

    count_services_up=$(echo "$output" | grep -c "running")
    assert [ "$count_services_up" -gt 1 ]

    for header in NAME VERSION STATUS PORT "PORT RANGE"; do
        assert_line --partial "$header"
    done

    # Para tudo
    for service in db attention-broker query-agent; do
        das-cli "$service" stop
    done

    sleep 5

    for container in "${services_containers[@]}"; do
        run is_service_up "$container"
        assert_failure
    done

    # Verifica status com tudo parado
    run das-cli system status

    count_services_up=$(echo "$output" | grep -c "running" || true)
    assert [ "$count_services_up" -eq 0 ]
}