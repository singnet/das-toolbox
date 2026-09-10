#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

safe_stop() {
    das-cli "$1" stop >/dev/null 2>&1 || true
}

QUERY_SIMILARITY_HUMAN='LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S'
QUERY_READY_MAX_ATTEMPTS=20
SERVICE_READY_MAX_ATTEMPTS=20

print_query_stack_diagnostics() {
    echo "---- query stack diagnostics ----"
    echo "docker ps -a"
    docker ps -a || true
    echo

    for container in das-command-router-40008 das-query-engine-40002; do
        echo "docker logs ${container} (last 200 lines)"
        docker logs --tail 200 "$container" 2>&1 || true
        echo
    done
}

wait_for_service_up() {
    local container_name="$1"
    local attempt=1

    while [ "$attempt" -le "$SERVICE_READY_MAX_ATTEMPTS" ]; do
        if is_service_up "$container_name"; then
            return 0
        fi

        sleep 1
        attempt=$((attempt + 1))
    done

    echo "Container '${container_name}' was not running after ${SERVICE_READY_MAX_ATTEMPTS} attempts."
    print_query_stack_diagnostics
    return 1
}

wait_for_query_ready() {
    local attempt=1
    local probe_output=""

    while [ "$attempt" -le "$QUERY_READY_MAX_ATTEMPTS" ]; do
        probe_output="$(das-cli query run "${QUERY_SIMILARITY_HUMAN}" 2>&1)"
        if [ "$?" -eq 0 ]; then
            return 0
        fi

        if [[ "$probe_output" == *"pattern_matching_query"* ]] || [[ "$probe_output" == *"Exception thrown in command processor."* ]]; then
            sleep 1
            attempt=$((attempt + 1))
            continue
        fi

        echo "$probe_output"
        return 1
    done

    echo "$probe_output"
    return 1
}

start_query_run_stack() {
    das-cli query-agent start --port-range 12000:12100
    das-cli command-router start
    das-cli metta load "$test_fixtures_dir/metta/animals.metta" >/dev/null 2>&1 || true
}

ensure_query_run_stack() {
    start_query_run_stack

    run wait_for_service_up das-command-router-40008
    assert_success

    run wait_for_service_up das-query-engine-40002
    assert_success

    run wait_for_query_ready
    if [ "$status" -ne 0 ]; then
        print_query_stack_diagnostics
    fi
    assert_success
}

setup() {
    use_config "simple" || true

    query_agent_port="$(extract_port "$(get_config .agents.query.endpoint 2>/dev/null || echo localhost:40002)")"

    stop_listen_port "$query_agent_port" 2>/dev/null || true

    das-cli attention-broker start || true
    das-cli db start || true
    das-cli query-agent stop || true
}

teardown() {
    safe_stop query-agent
    safe_stop command-router
    stop_listen_port "$query_agent_port" 2>/dev/null || true

    safe_stop attention-broker
}

@test "Query help lists the run command" {
    run das-cli query --help

    assert_success
    assert_output --partial "query - Execute queries via command-router"
    assert_output --partial "run"
}


@test "Query run fails when query text argument is missing" {
    run das-cli query run

    assert_failure
    assert_output --partial "Missing argument 'QUERY_TEXT'"
}

@test "Query run rejects empty query text" {
    run das-cli query run "   "

    assert_failure
    assert_output --partial "Query text must not be empty"
}

@test "Query run fails when command-router is not running" {
    safe_stop command-router

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}"

    assert_failure
    assert_output --partial "Failed to create query execution"
}

@test "Query run succeeds and streams results" {
    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}"

    assert_success
    assert_output --partial "Streaming execution"
    assert_output --partial "completed successfully"
}

@test "Query run json output includes stream chunk and terminal statuses" {
    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}" --output-format json

    assert_success
    assert_output --partial '"type": "chunk"'
    assert_output --partial '"status": "completed"'
    assert_output --partial '"status": "success"'
}

@test "Query run succeeds with execution parameters loaded from config" {
    set_config ".agents.base_query.params.attention_correlation" 1
    set_config ".agents.base_query.params.attention_update" 3
    set_config ".agents.base_query.params.unique_assignment_flag" true
    set_config ".agents.query.params.count_flag" true
    set_config ".agents.query.params.positive_importance_flag" true

    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}"

    assert_success
    assert_output --partial "completed successfully"
}

@test "Query run count_flag from config changes the streamed JSON event shape" {
    set_config ".agents.base_query.params.max_answers" 1
    set_config ".agents.query.params.count_flag" true
    set_config ".agents.query.params.positive_importance_flag" false
    set_config ".agents.query.params.disregard_importance_flag" false
    set_config ".agents.query.params.unique_value_flag" false

    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}" --output-format json

    assert_success
    assert_output --partial '"status": "completed"'
    assert_output --partial '"total_items": 0'
    assert_output --partial '"status": "success"'
}