import re
import click
from sys import exit
from enum import Enum
from services import OpenFaaSContainerService, ImageService
from exceptions import (
    ContainerNotRunningException,
    DockerException,
    DockerDaemonException,
    NotFound,
)
from config import OPENFAAS_IMAGE_NAME


class FunctionEnum(Enum):
    QUERY_ENGINE = "queryengine"
    ATOM_DB = "atomdb"


@click.group(help="Manage OpenFaaS services.")
@click.pass_context
def faas(ctx):
    """
    This command group allows you to manage OpenFaaS services.
    """

    global config

    config = ctx.obj["config"]


@faas.command(help="Start an OpenFaaS service.")
@click.option(
    "--function",
    help="Specify the OpenFaaS function to start.",
    required=False,
    type=click.Choice([e.value for e in FunctionEnum]),
    default=FunctionEnum.QUERY_ENGINE.value,
)
@click.option(
    "--version",
    help="Specify the version of the OpenFaaS function (format: x.x.x).",
    required=False,
    type=str,
    default="latest",
)
def start(function, version):
    """
    Start an OpenFaaS service.
    """
    if version != "latest" and not re.match(r"\d+\.\d+\.\d+", version):
        click.secho("The version must follow the format x.x.x (e.g 1.10.9)", fg="red")
        exit(1)

    openfaas_container_name = config.get("openfaas.container_name")
    redis_container_name = config.get("redis.container_name")
    mongodb_container_name = config.get("mongodb.container_name")
    services_not_running = False
    function_tag = f"{version}-{function}"

    redis_port = config.get("redis.port")
    mongodb_port = config.get("mongodb.port")

    try:
        container_service = OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        )
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)

    if not container_service.redis_container.is_running():
        click.secho("Redis is not running", fg="red")
        services_not_running = True
    else:
        click.secho(
            f"Redis is running on port {redis_port}",
            fg="yellow",
        )

    if not container_service.mongodb_container.is_running():
        click.secho("MongoDB is not running", fg="red")
        services_not_running = True
    else:
        click.secho(
            f"MongoDB is running on port {mongodb_port}",
            fg="yellow",
        )

    mongodb_username = config.get("mongodb.username")
    mongodb_password = config.get("mongodb.password")

    try:
        if services_not_running:
            raise ContainerNotRunningException(
                "\nPlease use 'server start' to start required services before running 'faas start'."
            )

        click.echo("Starting OpenFaaS...")

        ImageService.get_instance().pull(
            repository=OPENFAAS_IMAGE_NAME,
            image_tag=function_tag,
        )

        container_service.start_container(
            function,
            version,
            redis_port,
            mongodb_port,
            mongodb_username,
            mongodb_password,
        )

        click.secho(f"You are running the version '{version}' of the function.", fg="green")
        click.secho(f"OpenFaaS running on port 8080", fg="green")
    except (
        DockerException,
        ContainerNotRunningException,
        DockerDaemonException,
        NotFound,
    ) as e:
        click.secho(f"{str(e)}\n", fg="red")
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
        click.echo(f"Stopping OpenFaaS service...")
        OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        ).stop()
        click.secho("OpenFaaS service stopped", fg="green")
    except NotFound:
        click.secho(
            f"The OpenFaaS service named {openfaas_container_name} is already stopped.",
            fg="yellow",
        )
    except (DockerException, DockerDaemonException) as e:
        click.secho(
            f"\nError occurred while trying to stop OpenFaaS\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)
