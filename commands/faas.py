import click
from config import Config
from enum import Enum
from services.container import OpenFaaSContainerService
from exceptions import ContainerAlreadyRunningException


class FunctionEnum(Enum):
    QUERY_ENGINE = "queryengine"
    ATOM_DB = "atomdb"


@click.group()
def faas():
    global config

    config = Config()

    if not config.is_ready():
        click.echo(
            "Configuration is not ready. Please initialize the configuration first."
        )
        exit(1)


@faas.command()
@click.option(
    "--function",
    help="",
    required=True,
    type=click.Choice([e.value for e in FunctionEnum]),
)
@click.option(
    "--version",
    help="",
    required=True,
    type=str,
)
def start(function, version):
    redis_port = config.get("redis.port")
    mongodb_port = config.get("mongodb.port")
    mongodb_username = config.get("mongodb.username")
    mongodb_password = config.get("mongodb.password")
    external_port = 8080
    repository = "trueagi/das"
    services_not_running = False

    container_service = OpenFaaSContainerService()

    if not container_service.redis_container.container_running():
        click.echo("Redis is not running")
        services_not_running = True
    else:
        click.echo(f"Redis is running on port {config.get('redis.port')}")

    if not container_service.mongodb_container.container_running():
        click.echo("MongoDB is not running")
        services_not_running = True
    else:
        click.echo(f"MongoDB is running on port {config.get('mongodb.port')}")

    if services_not_running:
        click.echo(
            "\nPlease use 'server start' to start required services before running 'faas start'."
        )
        exit(1)

    try:
        click.echo("Starting FaaS...")

        container_service.start_container(
            repository,
            function,
            version,
            external_port,
            redis_port,
            mongodb_port,
            mongodb_username,
            mongodb_password,
        )

        click.echo(f"FaaS running on port {external_port}")
    except ContainerAlreadyRunningException:
        click.echo("FaaS Service is already running")
        exit(1)
    except Exception as e:
        click.echo(
            f"Error occurred while trying to start FaaS service on port {external_port}"
        )
        click.echo(f"Error Details: {str(e)}")
        click.echo(
            f"For more information, check the logs using the command 'docker logs das-openfaas' in your terminal."
        )
        exit(1)


@faas.command()
def stop():
    try:
        click.echo(f"Stopping/Removing OpenFaaS Service")
        OpenFaaSContainerService().stop()
        click.echo(f"Done.")
    except Exception as e:
        click.echo(f"Error Details: {str(e)}")
        exit(1)
