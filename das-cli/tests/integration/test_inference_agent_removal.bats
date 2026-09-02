#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'
load 'libs/docker'
load 'libs/errors'

# Regression tests to ensure inference-agent module remains removed from CLI
# This prevents accidental re-introduction of the module in future changes

setup() {
    use_config "simple"
    stop_simple_stack
}

teardown() {
    stop_simple_stack
}

@test "Configuration does not contain inference-agent section" {
    use_config "simple"
    
    # Verify that the config does not have inference-agent agent configuration
    run get_config ".agents.inference"
    assert_success
    assert_output "null"
}

@test "Config list succeeds without inference-agent configuration" {
    use_config "simple"
    
    # Config list should work without inference-agent present
    run das-cli config list
    assert_success
}

@test "System status works without inference-agent" {
    use_config "simple"
    
    # System status should succeed and not reference inference-agent
    run das-cli system status
    assert_success
    refute_output --partial "inference"
}

@test "Database service starts successfully without inference-agent" {
    use_config "simple"
    
    run das-cli db start
    assert_success
}

@test "Attention broker service starts without inference dependencies" {
    use_config "simple"
    
    run das-cli attention-broker start
    assert_success
}

@test "Query agent service starts without inference dependencies" {
    use_config "simple"
    
    run das-cli db start
    assert_success

    run das-cli attention-broker start
    assert_success

    run das-cli query-agent start
    assert_success
}

@test "CLI help does NOT expose the removed inference-agent command" {
    run das-cli --help
    assert_success
    refute_output --partial "inference-agent"
}

@test "Logs help does NOT expose inference-agent service" {
    run das-cli logs --help
    assert_success
    refute_output --partial "inference-agent"
}

@test "Attempting to use inference-agent command fails as expected" {
    run das-cli inference-agent --help
    assert_failure
    assert_output --partial "No such command"
}

@test "Attempting to view inference-agent logs fails as expected" {
    run das-cli logs inference-agent
    assert_failure
    assert_output --partial "No such command 'inference-agent'"
}
