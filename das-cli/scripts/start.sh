#!/bin/bash

containerd --log-level debug > /dev/null 2>&1 &
sleep 10s

dockerd > /dev/null 2>&1 &
sleep 10s

exec make "$@"
