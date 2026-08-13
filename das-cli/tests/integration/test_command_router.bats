#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'


safe_reset_command_router() {
    das-cli command-router stop >/dev/null 2>&1 || true
    sleep 0.2
}


setup() {
    use_config "simple"
    das-cli db start

    safe_reset_command_router
}


teardown() {
    das-cli command-router stop >/dev/null 2>&1 || true
}


@test "Trying to start, stop and restart command-router with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli command-router "$cmd"
        assert_output --partial "$FILE_NOT_FOUND_ERROR"
    done
}


@test "Start command-router when port is already in use" {
    use_config "simple"

    local endpoint="$(get_config .agents.command_router.endpoint)"
    local port="$(extract_port "$endpoint")"

    run listen_port "${port}"
    assert_success

    safe_reset_command_router

    run das-cli command-router start

    assert_failure 1
    assert_output --partial "Starting Command Router service..."
    assert_output --partial "$CONTAINER_START_FAILURE_MESSAGE"

    run stop_listen_port "${port}"
    assert_success

    run is_service_up das-command-router-40008
    assert_failure
}


@test "Starting command-router when it's already up" {
    use_config "simple"

    local endpoint="$(get_config .agents.command_router.endpoint)"
    local port="$(extract_port "$endpoint")"

    safe_reset_command_router

    das-cli command-router start

    run das-cli command-router start

    assert_output "Starting Command Router service...
Command Router is already running. It's listening on port ${port}"
}


@test "Starting the command-router" {
    use_config "simple"

    local endpoint="$(get_config .agents.command_router.endpoint)"
    local port="$(extract_port "$endpoint")"

    safe_reset_command_router

    run das-cli command-router start

    assert_output "Starting Command Router service...
Command Router started on port ${port}"

    run is_service_up das-command-router-40008
    assert_success
}


@test "Stopping command-router when it's up-and-running" {
    use_config "simple"

    safe_reset_command_router

    das-cli command-router start

    run das-cli command-router stop

    assert_output "Stopping Command Router service...
Command Router service stopped"
}


@test "Stopping command-router when it's already stopped" {
    use_config "simple"

    run das-cli command-router stop

    assert_output "Stopping Command Router service...
The Command Router service named das-command-router-40008 is already stopped."

    run is_service_up das-command-router-40008
    assert_failure
}


@test "Restarting command-router when it's up-and-running" {
    use_config "simple"

    local endpoint="$(get_config .agents.command_router.endpoint)"
    local port="$(extract_port "$endpoint")"

    safe_reset_command_router

    das-cli command-router start

    run das-cli command-router restart

    assert_output "Stopping Command Router service...
Command Router service stopped
Starting Command Router service...
Command Router started on port ${port}"

    run is_service_up das-command-router-40008
    assert_success
}


@test "Restarting command-router when it's not up" {
    use_config "simple"

    local endpoint="$(get_config .agents.command_router.endpoint)"
    local port="$(extract_port "$endpoint")"

    safe_reset_command_router

    run das-cli command-router restart

    assert_output --partial "Stopping Command Router service...
The Command Router service named das-command-router-40008 is already stopped.
Starting Command Router service...
Command Router started on port ${port}"

    run is_service_up das-command-router-40008
    assert_success
}
