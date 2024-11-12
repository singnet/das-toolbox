#!/bin/bash

function show_help {
    echo "Usage: ./stop_postgres.sh [options]"
    echo ""
    echo "Options:"
    echo "  -n, --name           Container name"
    echo "  -h, --help           Show this help message"
    exit 1
}

function main() {
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -n|--name) POSTGRES_CONTAINER_NAME="$2"; shift ;;
            -h|--help) show_help ;;
            *) echo "Unknown option: $1"; show_help ;;
        esac
        shift
    done

    if [[ -z "$POSTGRES_CONTAINER_NAME" ]]; then
        echo "Error: All required parameters must be provided."
        show_help
    fi

    if [ "$(docker ps -q -f name=$POSTGRES_CONTAINER_NAME)" ]; then
        docker rm -f "$POSTGRES_CONTAINER_NAME"
        echo "Container $POSTGRES_CONTAINER_NAME stopped successfully!"
    else
        echo "Container $POSTGRES_CONTAINER_NAME is not running..."
    fi
}

main "$@"
