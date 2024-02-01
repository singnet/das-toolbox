import click
from services.container import (
    RedisContainerService,
    MongoContainerService,
    CanonicalLoadContainerService,
    OpenFaaSContainerService,
)
from config import Config
from exceptions import ContainerNotRunningException, ContainerAlreadyRunningException


@click.group()
def server():
    global config

    config = Config()

    if not config.is_ready():
        click.echo(
            "Configuration is not ready. Please initialize the configuration first."
        )
        exit(1)


@server.command()
def start():
    try:
        click.echo("Starting Redis and MongoDB...")

        redis_service = RedisContainerService()

        redis_port = config.get("redis.port")
        mongodb_port = config.get("mongodb.port")
        mongodb_username = config.get("mongodb.username")
        mongodb_password = config.get("mongodb.password")

        redis_service.start_container(
            redis_port,
        )

        click.echo(f"Redis server running on port {redis_port}")

        mongodb_service = MongoContainerService()

        mongodb_service.start_container(
            mongodb_port,
            mongodb_username,
            mongodb_password,
        )

        click.echo(f"MongoDB server running on port {mongodb_port}")

        click.echo("Done.")
    except ContainerAlreadyRunningException:
        click.echo("Redis or MongoDB are already running. No further action needed.")
        exit(1)


@server.command()
@click.option(
    "--metta-path",
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
def load(metta_path, canonical):
    try:
        CanonicalLoadContainerService().stop()

        click.echo("Loading metta file(s)...")
        CanonicalLoadContainerService().start_container(
            metta_path,
            canonical,
            mongodb_port=config.get("mongodb.port"),
            mongodb_username=config.get("mongodb.username"),
            mongodb_password=config.get("mongodb.password"),
            redis_port=config.get("redis.port"),
        )
        click.echo("Done.")
    except ContainerNotRunningException:
        click.echo(
            "Redis or MongoDB is not running. Please use 'server start' to start the required services before running 'server load'."
        )
        exit(1)
    except FileNotFoundError:
        click.echo(f"The specified path '{metta_path}' does not exist.")
        exit(1)


@server.command()
def stop():
    click.echo(f"Stopping/Removing Currently Running Services")
    OpenFaaSContainerService().stop()
    CanonicalLoadContainerService().stop()
    MongoContainerService().stop()
    RedisContainerService().stop()
    click.echo(f"Done.")
