#!/usr/local/bin/bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'

@test "Show local examples" {

    run das-cli example local

    assert_success
}
