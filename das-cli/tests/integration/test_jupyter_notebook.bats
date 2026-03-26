#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

setup() {
    use_config "simple"

    jupyter_notebook_endpoint="$(get_config .environment.jupyter.endpoint)"
    jupyter_notebook_port="$(extract_port "$jupyter_notebook_endpoint")"

    jupyter_notebook=das-cli-jupyter-notebook-40019

    das-cli jupyter-notebook stop
}

teardown() {
    das-cli jupyter-notebook stop
}

@test "Trying to start, stop and restart Jupyter notebook with unset configuration file" {
    local cmds=(start stop restart)

    unset_config

    for cmd in "${cmds[@]}"; do
        run das-cli jupyter-notebook $cmd

        assert_output "[31m[FileNotFoundError] Configuration file not found in ${das_config_file}. You can run the command \`config set\` to create a configuration file.[39m"
    done
}

@test "Starting Jupyter notebook server" {
    run das-cli jupyter-notebook start

    assert_output "Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up $jupyter_notebook

    assert_success
}

@test "Starting Jupyter notebook server with relative working directory" {
    local jupyter_dir="$(mktemp -d)"
    local relative_jupyter_dir_path="relative"

    mkdir -p "$jupyter_dir/$relative_jupyter_dir_path"

    cd "$jupyter_dir"

    run das-cli jupyter-notebook start --working-dir $relative_jupyter_dir_path

    cd -

    assert_failure
    assert_line --partial "The path must be absolute."
}

@test "Starting Jupyter notebook server with working directory" {
    local jupyter_dir="$(mktemp -d)"

    run das-cli jupyter-notebook start --working-dir $jupyter_dir

    assert_output "Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up $jupyter_notebook

    assert_success
}

@test "Trying to start Jupyter notebook server after it has being started" {
    das-cli jupyter-notebook start

    run das-cli jupyter-notebook start

    assert_output "Starting Jupyter Notebook...
Jupyter Notebook is already running. It's listening on port $jupyter_notebook_port"

    run is_service_up $jupyter_notebook

    assert_success
}

@test "Stopping Jupyter notebook server" {
    das-cli jupyter-notebook start

    run das-cli jupyter-notebook stop

    assert_output "Stopping jupyter notebook...
Jupyter Notebook service stopped"

    run is_service_up $jupyter_notebook

    assert_failure
}

@test "Trying to stop Jupyter notebook server after has already being stopped" {
    run das-cli jupyter-notebook stop

    assert_output "Stopping jupyter notebook...
The Jupyter Notebook service named $jupyter_notebook is already stopped."

    run is_service_up $jupyter_notebook

    assert_failure
}

@test "Restarting Jupyter notebook server" {
    das-cli jupyter-notebook start

    run das-cli jupyter-notebook restart

    assert_output "Stopping jupyter notebook...
Jupyter Notebook service stopped
Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up $jupyter_notebook

    assert_success
}

@test "Trying to restart Jupyter notebook server before start server" {
    run das-cli jupyter-notebook restart

    assert_output "Stopping jupyter notebook...
The Jupyter Notebook service named $jupyter_notebook is already stopped.
Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up $jupyter_notebook

    assert_success
}
