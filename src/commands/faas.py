import click
from config import Secret
from enum import Enum
from services import OpenFaaSContainerService
from exceptions import ContainerAlreadyRunningException
from sys import exit


class FunctionEnum(Enum):
    QUERY_ENGINE = "queryengine"
    ATOM_DB = "atomdb"


@click.group(help="Manage OpenFaaS services.")
def faas():
    """
    This command group allows you to manage OpenFaaS services.
    """

    global config

    config = Secret()

    if not config.exists():
        click.echo(
            "The configuration file does not exist. Please initialize the configuration file first by running the command config set."
        )
        exit(1)


@faas.command(help="Start an OpenFaaS service.")
@click.option(
    "--function",
    help="Specify the OpenFaaS function to start.",
    required=True,
    type=click.Choice([e.value for e in FunctionEnum]),
)
@click.option(
    "--version",
    help="Specify the version of the OpenFaaS function.",
    required=True,
    type=str,
)
def start(function, version):
    """
    Start an OpenFaaS service.
    """
    openfaas_container_name = config.get("openfaas.container_name")
    redis_container_name = config.get("redis.container_name")
    mongodb_container_name = config.get("mongodb.container_name")

    redis_port = config.get("redis.port")
    mongodb_port = config.get("mongodb.port")
    mongodb_username = config.get("mongodb.username")
    mongodb_password = config.get("mongodb.password")
    external_port = 8080
    repository = "trueagi/das"
    services_not_running = False

    container_service = OpenFaaSContainerService(
        openfaas_container_name,
        redis_container_name,
        mongodb_container_name,
    )

    if not container_service.redis_container.is_running():
        click.echo("Redis is not running")
        services_not_running = True
    else:
        click.echo(f"Redis is running on port {config.get('redis.port')}")

    if not container_service.mongodb_container.is_running():
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
        click.echo("Starting OpenFaaS...")

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

        click.echo(f"OpenFaaS running on port {external_port}")
    except ContainerAlreadyRunningException:
        click.echo("OpenFaaS service is already running")
        exit(1)
    except Exception as e:
        click.echo(
            f"Error occurred while trying to start OpenFaaS service on port {external_port}"
        )
        click.echo(f"Error Details: {str(e)}")
        click.echo(
            f"For more information, check the logs using the command 'docker logs das-openfaas' in your terminal."
        )
        exit(1)


@faas.command(help="Stop the running OpenFaaS service.")
def stop():
    """
    Stop the running OpenFaaS service.
    """
    openfaas_container_name = config.get("openfaas.container_name")
    redis_container_name = config.get("redis.container_name")
    mongodb_container_name = config.get("mongodb.container_name")

    try:
        click.echo(f"Stopping/Removing OpenFaaS Service")
        OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        ).stop()
        click.echo(f"Done.")
    except Exception as e:
        click.echo(f"Error Details: {str(e)}")
        exit(1)
