import re
import click
from sys import exit
from services import OpenFaaSContainerService, ImageService
from exceptions import (
    ContainerNotRunningException,
    DockerException,
    DockerDaemonException,
    NotFound,
)
from config import OPENFAAS_IMAGE_NAME
from enums import FunctionEnum


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


def _pull_image(repository, function, version):
    image_tag = ImageService.format_function_tag(function, version)

    ImageService.get_instance().pull(
        repository,
        image_tag,
    )


def _handle_exception(message):
    click.secho(f"{message}\n", fg="red")
    exit(1)


def _handle_not_found(container_name):
    click.secho(
        f"The OpenFaaS service named {container_name} is already stopped.",
        fg="yellow",
    )


@click.group()
@click.pass_context
def faas(ctx):
    """
    Manage OpenFaaS services.

    'das-cli faas' provides management commands for OpenFaaS using the DAS CLI including deployment of latest or specific versions, service start/stop/restart, among others.
    """

    global config_service

    config_service = ctx.obj["config"]


def _get_version() -> tuple:
    version = config_service.get("openfaas.version", "latest")
    function = config_service.get("openfaas.function", FunctionEnum.QUERY_ENGINE.value)

    try:
        _pull_image(OPENFAAS_IMAGE_NAME, function, version)

        label = ImageService.get_instance().get_label(
            repository=OPENFAAS_IMAGE_NAME,
            tag=ImageService.format_function_tag(function, version),
            label="fn.version",
        )

        return function, label
    except Exception as e:
        _handle_exception(str(e))


@faas.command()
def version():
    """
    Get OpenFaaS function version.

    'das-cli faas version' is used to display the current version of the DAS function in OpenFaaS. This command is particularly useful for checking the version of the deployed function, which can be helpful troubleshooting issues, or ensuring compatibility.

    .SH EXAMPLES

    This is an example illustrating how to retrieve the version of the function.

    $ das-cli faas version
    """
    function, version = _get_version()

    click.secho(f"{function} {version}", fg="green")


@faas.command()
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
def update_version(function, version):
    """
    Update an OpenFaaS service to a newer version.

    'das-cli update-version' allows you to update the version of your function in OpenFaaS. All available versions can be found at https://github.com/singnet/das-serverless-functions/releases. This command has two optional parameters. When executed without parameters, it will fetch the latest version of the 'query-engine' function and update it on your local server if a newer version is found. You can also specify the function you want to update in OpenFaaS (currently only 'query-engine' is available), and define the version of the function you want to use, as mentioned earlier.

    .SH EXAMPLES

    This is an example of how to update to the latest available function version.

    $ das-cli update-version

    This is an example of how to update the function you want to use (currently only `query-engine` is available).

    $ das-cli update-version --function query-engine

    This demonstrates updating the function version to a specific release. You need to specify the version in the semver format

    $ das-cli update-version --version 1.0.0
    """

    _validate_version(version)

    current_function_name, current_function_version = _get_version()

    try:
        _pull_image(OPENFAAS_IMAGE_NAME, function, version)

        config_service.set("openfaas.version", version)
        config_service.set("openfaas.function", function)
        config_service.save()

        newer_function_name, newer_function_version = _get_version()

        if (
            current_function_name != newer_function_name
            or current_function_version != newer_function_version
        ):
            click.secho(
                f"Function version successfully updated {current_function_name} {current_function_version} --> {newer_function_name} {newer_function_version}. You need to call 'faas restart' to start using the new version.",
                fg="green",
            )
        else:
            click.secho(
                f"Function {current_function_name} is already at version {current_function_version}",
                fg="yellow",
            )
    except Exception as e:
        _handle_exception(e)


@faas.command()
def restart():
    """
    Restart OpenFaaS service.

    'das-cli faas restart' restarts OpenFaaS server container. This is useful when you want to restart the function to apply configuration changes. During this process, there is typically a downtime until the function is running again and deemed healthy. This downtime occurs because the existing instance of the function needs to be stopped, and then a new instance needs to be started with the updated configuration or changes.

    .SH EXAMPLES

    This is an example of how to restart the execution of the faas function.

    $ das-cli faas restart
    """
    ctx = click.Context(faas)
    ctx.invoke(stop)
    ctx.invoke(start)


@faas.command()
def start():
    """
    Start OpenFaaS service.

    OpenFaaS, an open-source serverless computing platform, makes running functions in containers fast and simple. With this command, you can initialize the DAS remotely through a function in OpenFaaS, which can be run on your server or locally.

    If you've just installed the DAS CLI, the function will be executed using the latest version by default. However, if you want to specify a particular version, you can use the faas update-version command. Versions are available at https://github.com/singnet/das-serverless-functions/releases, or you can choose to leave it as latest, which will always use the latest available version.

    Since the function needs to communicate with databases, you need to run db start to establish this communication. Upon the first execution of the function, it might take a little longer as it needs to fetch the specified version and set everything up for you. Subsequent initializations will be faster unless you change the version, which will require the same process again to set everything up.

    After starting the function, you will receive a message on the screen with the function version and the port on which the function is being executed.

    .SH EXAMPLES

    This is an example of how to start the function.

    $ das-cli faas start
    """

    version = config_service.get("openfaas.version", "latest")
    function = config_service.get("openfaas.function", FunctionEnum.QUERY_ENGINE.value)

    openfaas_container_name = config_service.get("openfaas.container_name")
    redis_container_name = config_service.get("redis.container_name")
    mongodb_container_name = config_service.get("mongodb.container_name")

    redis_port = config_service.get("redis.port")
    mongodb_port = config_service.get("mongodb.port")

    try:
        container_service = OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        )
    except DockerDaemonException as e:
        _handle_exception(str(e))

    mongodb_username = config_service.get("mongodb.username")
    mongodb_password = config_service.get("mongodb.password")

    try:
        _check_service_running(container_service, redis_port, mongodb_port)

        click.echo("Starting OpenFaaS...")

        _pull_image(OPENFAAS_IMAGE_NAME, function, version)

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


@faas.command()
def stop():
    """
    Stop the running OpenFaaS service.

    'das-cli faas stop' allows you to stop the execution of the DAS function in OpenFaaS. This is useful for terminating the function's operation when it's no longer needed. After stopping the faas, the function will no longer be available and cannot be used with the DAS.

    .SH EXAMPLES

    This is an example of how to stop the function

    $ das-cli faas stop
    """
    openfaas_container_name = config_service.get("openfaas.container_name")
    redis_container_name = config_service.get("redis.container_name")
    mongodb_container_name = config_service.get("mongodb.container_name")

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
