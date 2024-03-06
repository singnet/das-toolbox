import click
import os
from services import MettaLoaderContainerService
from services import MettaSyntaxValidatorService
from config import Secret
from sys import exit


@click.group(help="Manage Metta operations.")
def metta():
    """
    This command group allows you to manage Metta operations.
    """

    global config

    config = Secret()

    if not config.exists():
        click.echo(
            "The configuration file does not exist. Please initialize the configuration file first by running the command config set."
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
        MettaLoaderContainerService(
            loader_container_name,
            redis_container_name,
            mongodb_container_name,
        ).stop()
        loader_service = MettaLoaderContainerService(
            loader_container_name,
            redis_container_name,
            mongodb_container_name,
        )

        if not loader_service.redis_container.is_running():
            click.echo("Redis is not running")
            services_not_running = True
        else:
            click.echo(f"Redis is running on port {config.get('redis.port')}")

        if not loader_service.mongodb_container.is_running():
            click.echo("MongoDB is not running")
            services_not_running = True
        else:
            click.echo(f"MongoDB is running on port {config.get('mongodb.port')}")

        if services_not_running:
            click.echo(
                "\nPlease use 'server start' to start required services before running 'server load'."
            )
            exit(1)

        click.echo("Loading metta file(s)...")

        loader_service.start_container(
            path,
            mongodb_port=config.get("mongodb.port"),
            mongodb_username=config.get("mongodb.username"),
            mongodb_password=config.get("mongodb.password"),
            redis_port=config.get("redis.port"),
        )
        click.echo("Done.")
    except FileNotFoundError:
        click.echo(f"The specified path '{path}' does not exist.")
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

    metta_service = MettaSyntaxValidatorService()
    click.echo("Checking syntax...")

    if os.path.isdir(path):
        metta_service.validate_directory(path)
    else:
        metta_service.validate_file(path)
