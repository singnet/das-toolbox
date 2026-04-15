#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

setup() {
    use_config "simple"

    jupyter_notebook_port="$(extract_port "$(get_config .environment.jupyter.endpoint)")"
    jupyter_notebook="das-cli-jupyter-notebook-40019"

    # limpeza forte
    das-cli jupyter-notebook stop &>/dev/null || true
    stop_listen_port "$jupyter_notebook_port" &>/dev/null || true
}

teardown() {
    das-cli jupyter-notebook stop &>/dev/null || true
}

@test "Trying to start, stop and restart Jupyter notebook with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli jupyter-notebook "$cmd"
        assert_output --partial "$FILE_NOT_FOUND_ERROR"
    done
}

@test "Starting Jupyter notebook server" {
    run das-cli jupyter-notebook start

    assert_success
    assert_output --partial "Starting Jupyter Notebook"
    assert_output --partial "started on port"
    assert_output --partial "$jupyter_notebook_port"

    run is_service_up "$jupyter_notebook"
    assert_success
}

@test "Starting Jupyter notebook server with relative working directory" {
    local jupyter_dir
    jupyter_dir="$(mktemp -d)"
    local relative_path="relative"

    mkdir -p "$jupyter_dir/$relative_path"

    cd "$jupyter_dir"

    run das-cli jupyter-notebook start --working-dir "$relative_path"

    cd - &>/dev/null

    assert_failure
    assert_output --partial "must be absolute"
}

@test "Starting Jupyter notebook server with working directory" {
    local jupyter_dir
    jupyter_dir="$(mktemp -d)"

    run das-cli jupyter-notebook start --working-dir "$jupyter_dir"

    assert_success
    assert_output --partial "started on port"
    assert_output --partial "$jupyter_notebook_port"

    run is_service_up "$jupyter_notebook"
    assert_success
}

@test "Trying to start Jupyter notebook server after it has been started" {
    # garante estado válido
    run das-cli jupyter-notebook start
    assert_success

    run das-cli jupyter-notebook start

    assert_output --partial "already running"
    assert_output --partial "$jupyter_notebook_port"

    run is_service_up "$jupyter_notebook"
    assert_success
}

@test "Stopping Jupyter notebook server" {
    das-cli jupyter-notebook start

    run das-cli jupyter-notebook stop

    assert_output --partial "service stopped"

    run is_service_up "$jupyter_notebook"
    assert_failure
}

@test "Trying to stop Jupyter notebook server after already stopped" {
    run das-cli jupyter-notebook stop

    assert_output --partial "already stopped"

    run is_service_up "$jupyter_notebook"
    assert_failure
}

@test "Restarting Jupyter notebook server" {
    das-cli jupyter-notebook start

    run das-cli jupyter-notebook restart

    assert_output --partial "Stopping"
    assert_output --partial "Starting Jupyter Notebook"
    assert_output --partial "$jupyter_notebook_port"

    run is_service_up "$jupyter_notebook"
    assert_success
}

@test "Trying to restart Jupyter notebook server before start server" {
    run das-cli jupyter-notebook restart

    assert_output --partial "already stopped"
    assert_output --partial "Starting Jupyter Notebook"
    assert_output --partial "$jupyter_notebook_port"

    run is_service_up "$jupyter_notebook"
    assert_success
}