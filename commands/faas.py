import click
from services.container import ContainerService
from config import Config
from exceptions import ContainerAlreadyRunningException, ContainerNotRunningException
from enum import Enum


class FunctionEnum(Enum):
    QUERY_ENGINE = "queryengine"
    ATOM_DB = "atomdb"


@click.group()
def faas():
    global container_service
    global config_service

    config_service = Config()
    container_service = ContainerService()

    config_service.load()
    if not config_service.is_config_ready():
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
    redis_port = config_service.get("redis.port")
    mongodb_port = config_service.get("mongodb.port")
    mongodb_username = config_service.get("mongodb.username")
    mongodb_password = config_service.get("mongodb.password")
    external_port = 8080
    repository = "trueagi/das"

    try:
        click.echo("Starting FaaS...")

        container_service.setup_openfaas(
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
    container_service.prune()
