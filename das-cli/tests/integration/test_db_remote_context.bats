#!/usr/bin/env bats

load 'libs/bats-support/load'
load 'libs/bats-assert/load'
load 'libs/utils'

setup() {
    use_config "simple"
}

configure_remote_peer_without_context() {
    local updated
    updated="$(mktemp)"
    jq '
        .atomdb.type = "remotedb"
        | .atomdb.remote_peers = [{
            uid: "peer1",
            type: "redismongodb",
            context: "remotedb_peer1_",
            redis: {endpoint: "10.1.0.8:40020", cluster: false},
            mongodb: {
                endpoint: "10.1.0.8:40021",
                username: "admin",
                password: "admin",
                cluster: false
            }
        }]
    ' "$das_config_file" > "$updated"
    mv "$updated" "$das_config_file"
}

@test "db start and stop fail when a remote peer has no Docker context" {
    configure_remote_peer_without_context

    run das-cli db start
    assert_failure
    assert_output --partial "Redis node 10.1.0.8 has no Docker context"
    assert_output --partial "MongoDB node 10.1.0.8 has no Docker context"

    run das-cli db stop
    assert_failure
    assert_output --partial "Redis node 10.1.0.8 has no Docker context"
    assert_output --partial "MongoDB node 10.1.0.8 has no Docker context"
}
