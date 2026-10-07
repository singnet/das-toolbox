#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

QUERY_SIMILARITY_HUMAN='LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S'
STACK_CONTAINERS=(das-cli-authorization-admin das-command-router-40008 das-query-engine-40002 das-attention-broker-40001 das-cli-redis-40020 das-cli-mongodb-40021)

print_diagnostics() {
    local container
    echo '---- protected query diagnostics ----' >&2
    if [[ -f "$das_config_file" ]]; then
        jq '{atomdb: {uid: .atomdb.uid, public_keys: .atomdb.public_keys}, agents: {base_query: .agents.base_query, query: .agents.query}}' "$das_config_file" >&2 || true
    fi
    if [[ -n "${test_state_dir:-}" ]]; then
        for diagnostic in "$test_state_dir/query.json" "$test_state_dir/query.stderr"; do
            [[ ! -f "$diagnostic" ]] || tail -n 200 "$diagnostic" >&2
        done
    fi
    for container in "${STACK_CONTAINERS[@]}"; do
        echo "---- $container ----" >&2
        docker logs --tail 200 "$container" >&2 2>&1 || true
    done
}

query_completed() {
    jq -e -s '
        any(.[]; .status == "completed") and
        (last | .status == "success") and
        all(.[]; .status != "error" and .status != "aborted")
    ' "$test_state_dir/query.json" >/dev/null
}

query_authorized() {
    query_completed && jq -e -s '
        [.[] | select(.type == "chunk") | .data[]? | .. | strings] |
        any(.[]; contains("chimp"))
    ' "$test_state_dir/query.json" >/dev/null
}

query_without_results() {
    query_completed && jq -e -s '
        [.[] | select(.type == "chunk") | .data[]?] | length == 0
    ' "$test_state_dir/query.json" >/dev/null
}

execute_query() {
    timeout 30 das-cli query run "$QUERY_SIMILARITY_HUMAN" --output-format json \
        >"$test_state_dir/query.json" 2>"$test_state_dir/query.stderr"
}

wait_for_authorized_query() {
    local deadline=$((SECONDS + 180))
    while ((SECONDS < deadline)); do
        if execute_query && query_authorized; then
            return 0
        fi
    done
    print_diagnostics
    return 1
}

grant_primary_key() {
    local image
    cp "$das_config_file" "$test_state_dir/admin.json" || return 1
    image="$(docker container inspect --format '{{.Image}}' das-attention-broker-40001)" || return 1
    run_authorization_admin "$image" "$test_state_dir/admin.json" \
        grant --public-key valid_primary_key --full-access
}

setup() {
    test_state_dir="$(mktemp -d /tmp/das-cli-protected-atomdb.XXXXXX)" || return 1
    if [[ -f "$das_config_file" ]]; then
        cp -p "$das_config_file" "$test_state_dir/original-config.json" || return 1
    fi
    if [[ -f "$das_env_file" ]]; then
        cp -p "$das_env_file" "$test_state_dir/original.env" || return 1
    fi
    configuration_saved=1
    use_config simple || return 1
    stack_owned=1
    stop_simple_stack --prune || return 1
    local port
    for port in 40001 40002 40008 40009 40020 40021; do
        if lsof -iTCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "Port $port is occupied by a process outside the test stack." >&2
            return 1
        fi
    done
    set_config '.atomdb.public_keys' '["valid_primary_key"]' || return 1
    set_config '.agents.base_query.params.public_key_tokens' '""' || return 1
    set_config '.agents.base_query.params.populate_metta_mapping' true || return 1
    run timeout 180 das-cli attention-broker start
    assert_success
    run timeout 180 das-cli db start
    assert_success
    run timeout 180 das-cli metta load "$test_fixtures_dir/metta/animals.metta"
    assert_success
    run grant_primary_key
    assert_success
    assert_output --partial 'Admin finished successfully.'
    run timeout 180 das-cli query-agent start --port-range 12000:12100
    assert_success
    run timeout 180 das-cli command-router start
    assert_success
    wait_for_authorized_query
}

teardown() {
    local cleanup_status=0
    if [[ "${stack_owned:-}" == 1 ]]; then
        [[ "${BATS_TEST_COMPLETED:-}" == 1 ]] || print_diagnostics
        stop_simple_stack --prune || cleanup_status=1
    fi
    if [[ "${configuration_saved:-}" == 1 ]]; then
        if [[ -f "$test_state_dir/original-config.json" ]]; then
            cp -p "$test_state_dir/original-config.json" "$das_config_file" || cleanup_status=1
        else
            rm -f "$das_config_file" || cleanup_status=1
        fi
        if [[ -f "$test_state_dir/original.env" ]]; then
            cp -p "$test_state_dir/original.env" "$das_env_file" || cleanup_status=1
        else
            rm -f "$das_env_file" || cleanup_status=1
        fi
    fi
    [[ -z "${test_state_dir:-}" ]] || rm -rf "$test_state_dir" || cleanup_status=1
    return "$cleanup_status"
}

@test "Protected query uses the first configured public key" {
    set_config '.atomdb.public_keys' '["valid_primary_key", "valid_secondary_key"]'
    run execute_query
    assert_success
    run query_authorized
    assert_success
}

@test "Protected query does not fall back to the second public key" {
    set_config '.atomdb.public_keys' '["invalid_key", "valid_primary_key"]'
    run execute_query
    assert_success
    run query_without_results
    assert_success

    set_config '.atomdb.public_keys' '["valid_primary_key"]'
    run execute_query
    assert_success
    run query_authorized
    assert_success
}

@test "Protected query respects explicit public_key_tokens over derived keys" {
    set_config '.atomdb.public_keys' '["invalid_key", "valid_primary_key"]'
    set_config '.agents.base_query.params.public_key_tokens' '"local valid_primary_key"'
    run execute_query
    assert_success
    run query_authorized
    assert_success
}

@test "Protected query returns no results without a configured public key" {
    set_config '.atomdb.public_keys' '[]'
    set_config '.agents.base_query.params.public_key_tokens' '""'
    run execute_query
    assert_success
    run query_without_results
    assert_success

    set_config '.atomdb.public_keys' '["valid_primary_key"]'
    run execute_query
    assert_success
    run query_authorized
    assert_success
}