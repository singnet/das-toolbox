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


def _validate_version(version):
    if version != "latest" and not re.match(r"v?\d+\.\d+\.\d+", version):
        click.secho("The version must follow the format x.x.x (e.g 1.10.9)", fg="red")
        exit(1)


def _check_service_running(container_service, redis_port, mongodb_port):
    services_not_running = False

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

    if services_not_running:
        raise ContainerNotRunningException(
            "\nPlease use 'db start' to start required services before running 'faas start'."
        )


def _pull_image(repository, image_tag):
    ImageService.get_instance().pull(
        repository=repository,
        image_tag=image_tag,
    )


def _handle_exception(message):
    click.secho(f"{message}\n", fg="red")
    exit(1)


def _handle_not_found(container_name):
    click.secho(
        f"The OpenFaaS service named {container_name} is already stopped.",
        fg="yellow",
    )


@click.group(help="Manage OpenFaaS services.")
@click.pass_context
def faas(ctx):
    """
    This command group allows you to manage OpenFaaS services.
    """

    global config

    config = ctx.obj["config"]


@faas.command(help="Restart OpenFaaS service.")
def restart():
    ctx = click.Context(faas)
    ctx.invoke(stop)
    ctx.invoke(start)


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
)
def start(function, version):
    """
    Start an OpenFaaS service.
    """
    version = version or config.get("openfaas.version", "latest")

    _validate_version(version)

    openfaas_container_name = config.get("openfaas.container_name")
    redis_container_name = config.get("redis.container_name")
    mongodb_container_name = config.get("mongodb.container_name")

    redis_port = config.get("redis.port")
    mongodb_port = config.get("mongodb.port")

    try:
        container_service = OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        )
    except DockerDaemonException as e:
        _handle_exception(str(e))

    _check_service_running(container_service, redis_port, mongodb_port)

    mongodb_username = config.get("mongodb.username")
    mongodb_password = config.get("mongodb.password")

    try:
        click.echo("Starting OpenFaaS...")

        function_tag = f"{version}-{function}"
        _pull_image(OPENFAAS_IMAGE_NAME, function_tag)

        container_service.start_container(
            function,
            version,
            redis_port,
            mongodb_port,
            mongodb_username,
            mongodb_password,
        )

        label = container_service.get_label("fn.version") or version
        version_str = f"latest ({label})" if version == "latest" else label

        click.secho(
            f"You are running the version '{version_str}' of the function.",
            fg="green",
        )
        click.secho(f"OpenFaaS running on port 8080", fg="green")
    except Exception as e:
        _handle_exception(str(e))


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
        container_service = OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        )
        container_service.stop()
        click.secho("OpenFaaS service stopped", fg="green")
    except NotFound:
        _handle_not_found(openfaas_container_name)
    except (DockerException, DockerDaemonException) as e:
        _handle_exception(e)
