import click
from config import Config
from enum import Enum
from services.container import OpenFaaSContainerService
from exceptions import ContainerAlreadyRunningException, ContainerNotRunningException


class FunctionEnum(Enum):
    QUERY_ENGINE = "queryengine"
    ATOM_DB = "atomdb"


@click.group()
def faas():
    global container_service
    global config

    config = Config()
    container_service = OpenFaaSContainerService()

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
        click.echo("The FaaS container is already running")
        exit(1)
    except ContainerNotRunningException:
        click.echo(
            "Redis or MongoDB is not running. Please use 'server start' to start the required services before running 'faas start'."
        )
        exit(1)


@faas.command()
def stop():
    click.echo(f"Stopping/Removing OpenFaaS Service")
    OpenFaaSContainerService().stop()
    click.echo(f"Done.")
