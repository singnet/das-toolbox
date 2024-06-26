#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"

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
    local jupyter_notebook_port="$(get_config .jupyter_notebook.port)"

    run das-cli jupyter-notebook start

    assert_output "Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up jupyter_notebook

    assert_success
}

@test "Trying to start Jupyter notebook server after it has being started" {
    local jupyter_notebook_port="$(get_config .jupyter_notebook.port)"

    das-cli jupyter-notebook start

    run das-cli jupyter-notebook start

    assert_output "Starting Jupyter Notebook...
Jupyter Notebook is already running. It's listening on port $jupyter_notebook_port"

    run is_service_up jupyter_notebook

    assert_success
}

@test "Stopping Jupyter notebook server" {
    das-cli jupyter-notebook start

    run das-cli jupyter-notebook stop

    assert_output "Stopping jupyter notebook...
Jupyter Notebook service stopped"

    run is_service_up jupyter_notebook

    assert_failure
}

@test "Trying to stop Jupyter notebook server after has already being stopped" {
    local jupyter_notebook_container_name="$(get_config .jupyter_notebook.container_name)"

    run das-cli jupyter-notebook stop

    assert_output "Stopping jupyter notebook...
The Jupyter Notebook service named $jupyter_notebook_container_name is already stopped."

    run is_service_up jupyter_notebook

    assert_failure
}

@test "Restarting Jupyter notebook server" {
    local jupyter_notebook_port="$(get_config .jupyter_notebook.port)"

    das-cli jupyter-notebook start

    run das-cli jupyter-notebook restart

    assert_output "Stopping jupyter notebook...
Jupyter Notebook service stopped
Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up jupyter_notebook

    assert_success
}

@test "Trying to restart Jupyter notebook server before start server" {
    local jupyter_notebook_port="$(get_config .jupyter_notebook.port)"
    local jupyter_notebook_container_name="$(get_config .jupyter_notebook.container_name)"

    run das-cli jupyter-notebook restart

    assert_output "Stopping jupyter notebook...
The Jupyter Notebook service named $jupyter_notebook_container_name is already stopped.
Starting Jupyter Notebook...
Jupyter Notebook started on port $jupyter_notebook_port"

    run is_service_up jupyter_notebook

    assert_success
}
