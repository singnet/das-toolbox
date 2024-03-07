import os
import click
from sys import exit
from services import MettaLoaderContainerService
from services import MettaSyntaxValidatorService
from config import Secret, SECRETS_PATH, USER_DAS_PATH
from exceptions import DockerException, ContainerNotRunningException, DockerDaemonException


@click.group(help="Manage Metta operations.")
def metta():
    """
    This command group allows you to manage Metta operations.
    """

    global config

    try:
        config = Secret()
    except PermissionError:
        click.secho(
            f"\nWe apologize for the inconvenience, but it seems that you don't have the required permissions to write to {SECRETS_PATH}.\n\nTo resolve this, please make sure you are the owner of the file by running: `sudo chown $USER:$USER {USER_DAS_PATH} -R`, and then grant the necessary permissions using: `sudo chmod 770 {USER_DAS_PATH} -R`\n",
            fg="red",
        )
        exit(1)


@metta.command(help="Load a MeTTa file into the databases")
@click.option(
    "--path",
    help="Specify the path to the Metta file for loading.",
    required=True,
    type=str,
)
def load(path):
    """
    Load Metta file(s) into the Metta Loader service.
    """

    loader_container_name = config.get("loader.container_name")
    redis_container_name = config.get("redis.container_name")
    mongodb_container_name = config.get("mongodb.container_name")
    services_not_running = False

    try:
        loader_service = MettaLoaderContainerService(
            loader_container_name,
            redis_container_name,
            mongodb_container_name,
        )

        if not loader_service.redis_container.is_running():
            click.secho("Redis is not running", fg="red")
            services_not_running = True
        else:
            click.secho(
                f"Redis is running on port {config.get('redis.port')}",
                fg="yellow",
            )

        if not loader_service.mongodb_container.is_running():
            click.secho("MongoDB is not running", fg="red")
            services_not_running = True
        else:
            click.secho(
                f"MongoDB is running on port {config.get('mongodb.port')}",
                fg="yellow",
            )

        if services_not_running:
            raise ContainerNotRunningException(
                "\nPlease use 'server start' to start required services before running 'metta load'."
            )

        click.echo("Loading metta file(s)...")

        loader_service.start_container(
            path,
            mongodb_port=config.get("mongodb.port"),
            mongodb_username=config.get("mongodb.username"),
            mongodb_password=config.get("mongodb.password"),
            redis_port=config.get("redis.port"),
        )
        click.echo("Done.")
    except (
        DockerDaemonException,
        DockerException,
        ContainerNotRunningException,
        FileNotFoundError,
        IsADirectoryError,
    ) as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)


@metta.command(help="Validate the syntax of a Metta file or directory.")
@click.option(
    "--path",
    help="Specify the path to the Metta file or directory for validation.",
    required=True,
    type=str,
)
def validate(path: str):
    """
    Validate the syntax of a Metta file or directory.
    """

    try:
        metta_service = MettaSyntaxValidatorService()

        if os.path.isdir(path):
            metta_service.validate_directory(
                path,
            )
        else:
            metta_service.validate_file(path)
    except Exception as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)
