#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    local libs=(hyperon-das hyperon-das-atomdb das-serverless-functions das-metta-parser das-toolbox)
}

@test "Listing available modules version with release notes" {

    run das-cli release-notes

    for lib in "${libs[@]}"; do
        assert_line --partial "$lib: "
    done
}

@test "Listing available modules version without release notes" {

    run das-cli release-notes --list

    for lib in "${libs[@]}"; do
        assert_line --partial "$lib: "
    done
}

@test "Trying to show a nonexistent module" {
    local module_name="nonexistent=module"

    run das-cli release-notes --module $module_name

    assert_output "[31m[ReleaseNoteNotFound] Release note for $module_name not found[39m"
}

@test "Trying to show an invalid module name" {
    local module_name="invalid-module"

    run das-cli release-notes --module $module_name

    assert_output "[31m[ReleaseNoteNotFound] Release note for $module_name not found[39m"
}

@test "Show a module with changelog" {
    local module_regex="^.+:\s[0-9]+\.[0-9]+\.[0-9]+$"

    for lib in "${libs[@]}"; do
        run das-cli release-notes --module $lib

        match_count=$(echo "$output" | grep -cE $module_regex)

        refute_output --regexp $module_regex
        assert [ "$match_count" -eq 1 ]
    done

}

@test "Show a module without changelog" {
    local module_regex="^.+:\s[-9]+\.[0-9]+\.[0-9]+$"

    for lib in "${libs[@]}"; do
        run das-cli release-notes --module $lib --list

        match_count=$(echo "$output" | grep -cE $module_regex)

        assert_line --partial "$lib: "
        assert_output --regexp $module_regex
        assert [ "$match_count" -eq 1 ]
    done
}
