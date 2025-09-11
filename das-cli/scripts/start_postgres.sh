#!/bin/bash

function show_help {
    echo "Usage: ./start_postgres.sh [options]"
    echo ""
    echo "Options:"
    echo "  -n, --name           Container name"
    echo "  -p, --password       Password for the postgres user"
    echo "  -P, --port           PostgreSQL port"
    echo "  -v, --volume         Volume name for data persistence"
    echo "  -i, --initdb         Volume name for data initialization"
    echo "  -d, --dbname         Name of the initial database"
    echo "  -u, --username       Username for the initial database"
    echo "  -h, --help           Show this help message"
    exit 1
}

function main() {
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -n|--name) POSTGRES_CONTAINER_NAME="$2"; shift ;;
            -p|--password) POSTGRES_PASSWORD="$2"; shift ;;
            -P|--port) POSTGRES_PORT="$2"; shift ;;
            -d|--dbname) POSTGRES_DBNAME="$2"; shift ;;
            -u|--username) POSTGRES_USERNAME="$2"; shift ;;
            -i|--initdb) POSTGRES_DBINIT="$2"; shift ;;
            -h|--help) show_help ;;
            *) echo "Unknown option: $1"; show_help ;;
        esac
        shift
    done

    if [[ -z "$POSTGRES_CONTAINER_NAME" || -z "$POSTGRES_PASSWORD" || -z "$POSTGRES_PORT" || -z "$POSTGRES_DBNAME" || -z "$POSTGRES_USERNAME" || -z "$POSTGRES_DBINIT" ]]; then
        echo "Error: All required parameters must be provided."
        show_help
    fi

    if [[ ! -f "$POSTGRES_DBINIT" ]]; then
        echo "Error: --initdb | -i needs to be a valid file"
        exit 1
    fi

    if [ "$(docker ps -q -f name=$POSTGRES_CONTAINER_NAME)" ]; then
        echo "The container $POSTGRES_CONTAINER_NAME is already running."
    else
        docker run -d \
            --name "$POSTGRES_CONTAINER_NAME" \
            -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
            -e POSTGRES_DB="$POSTGRES_DBNAME" \
            -e POSTGRES_USER="$POSTGRES_USERNAME" \
            -e POSTGRES_PORT="$POSTGRES_PORT" \
            -p "$POSTGRES_PORT":"$POSTGRES_PORT" \
            -v "$POSTGRES_DBINIT:/docker-entrypoint-initdb.d/$(basename $POSTGRES_DBINIT)" \
            postgres:latest

        echo "Container $POSTGRES_CONTAINER_NAME started successfully!"
    fi
}

main "$@"
