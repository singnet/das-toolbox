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

start_query_run_stack() {
    das-cli command-router start >/dev/null 2>&1 || true
    das-cli query-agent start --port-range 12000:12100 >/dev/null 2>&1 || true
    das-cli metta load "$test_fixtures_dir/metta/animals.metta" >/dev/null 2>&1 || true
}

ensure_query_run_stack() {
    start_query_run_stack

    run is_service_up das-command-router-40008
    assert_success

    run is_service_up das-query-engine-40002
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

@test "Query run help lists parameter flags" {
    run das-cli query run --help

    assert_success
    assert_output --partial "--attention-correlation"
    assert_output --partial "--attention-update"
    assert_output --partial "--unique-assignment"
}

@test "Query run rejects invalid attention-correlation option value" {
    run das-cli query run "(Inheritance Link Human Mammal)" --attention-correlation INVALID

    assert_failure
    assert_output --partial "Invalid value for '--attention-correlation'"
}

@test "Query run rejects invalid attention-update option value" {
    run das-cli query run "(Inheritance Link Human Mammal)" --attention-update INVALID

    assert_failure
    assert_output --partial "Invalid value for '--attention-update'"
}

@test "Query run rejects invalid unique-assignment option value" {
    run das-cli query run "(Inheritance Link Human Mammal)" --unique-assignment maybe

    assert_failure
    assert_output --partial "Invalid value for '--unique-assignment'"
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

@test "Query run succeeds and returns expected similarity values" {
    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}"

    assert_success
    assert_output --partial "Streaming execution"
    assert_output --partial "completed successfully"

    if [[ ! "$output" =~ monkey|chimp|ent ]]; then
        echo "Expected at least one known Similarity answer for \"human\" (monkey|chimp|ent)."
        echo "$output"
        false
    fi
}

@test "Query run json output includes stream chunk and terminal statuses" {
    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}" --output-format json

    assert_success
    assert_output --partial '"type": "chunk"'
    assert_output --partial '"status": "completed"'
    assert_output --partial '"status": "success"'
}

@test "Query run succeeds with parameter override flags" {
    ensure_query_run_stack

    run das-cli query run "${QUERY_SIMILARITY_HUMAN}" \
        --attention-correlation HANDLES \
        --attention-update HANDLES_VARIABLES \
        --unique-assignment true

    assert_success
    assert_output --partial "completed successfully"
}