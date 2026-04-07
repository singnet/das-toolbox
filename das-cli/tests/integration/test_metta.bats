#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"
    das-cli db start
}

@test "Loading MeTTa file using MORK_MONGODB backend (skip redis)" {
    local metta_file_path="$test_fixtures_dir/metta/animals.metta"

    update_json_key "$das_config_file" "atomdb.backend" "morkmongodb"

    local mongodb_endpoint="$(get_config .atomdb.mongodb.endpoint)"
    local mongodb_port="$(extract_port "$mongodb_endpoint")"

    das-cli db start
    sleep 10s

    run das-cli metta load "$metta_file_path"

    assert_line --partial "das-cli-mongodb-${mongodb_port} is running on port ${mongodb_port}"

    assert_line --partial "Loading metta file ${metta_file_path}..."
    assert_line --partial "Done loading."

    assert_success
}