import click
from services.container import (
    CanonicalLoadContainerService,
    MettaParserContainerService,
)
from config import Config
from sys import exit
from exceptions import ValidateFailed


@click.group()
def metta():
    global config

    config = Config()

    if not config.exists():
        click.echo(
            "The configuration file does not exist. Please initialize the configuration file first by running the command config set."
        )
        exit(1)


@metta.command()
@click.option(
    "--path",
    help="",
    required=True,
    type=str,
)
@click.option(
    "--canonical",
    help="",
    required=False,
    is_flag=True,
    default=False,
)
def load(path, canonical):
    try:
        CanonicalLoadContainerService().stop()

        services_not_running = False
        canonical_load_service = CanonicalLoadContainerService()

        if not canonical_load_service.redis_container.container_running():
            click.echo("Redis is not running")
            services_not_running = True
        else:
            click.echo(f"Redis is running on port {config.get('redis.port')}")

        if not canonical_load_service.mongodb_container.container_running():
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
        canonical_load_service.start_container(
            path,
            canonical,
            mongodb_port=config.get("mongodb.port"),
            mongodb_username=config.get("mongodb.username"),
            mongodb_password=config.get("mongodb.password"),
            redis_port=config.get("redis.port"),
        )
        click.echo("Done.")
    except FileNotFoundError:
        click.echo(f"The specified path '{path}' does not exist.")
        exit(1)


@metta.command()
@click.option(
    "--filepath",
    help="",
    required=True,
    type=str,
)
def validate(filepath: str):
    metta_parser_service = MettaParserContainerService()

    try:
        click.echo("Checking if the Metta file is valid...")
        metta_parser_service.start_container(filepath)

        click.echo("The Metta file is valid.")
    except FileNotFoundError:
        click.echo(f"The specified file path '{filepath}' does not exist.")
        exit(1)
    except ValidateFailed:
        click.echo(f"The file '{filepath}' is not a valid Metta file.")
        exit(1)
