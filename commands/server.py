import click
from services.container import ContainerService
from services.config import ConfigService
from exceptions import ContainerNotRunningException, ContainerAlreadyRunningException


@click.group()
def server():
    global container_service
    global config_service

    container_service = ContainerService()
    config_service = ConfigService()
    config_service.load()

    if not config_service.is_config_ready():
        click.echo(
            "Configuration is not ready. Please initialize the configuration first."
        )
        exit(1)


@server.command()
def start():
    try:
        click.echo("Starting Redis and MongoDB...")

        redis_port = config_service.get("redis.port")
        mongodb_port = config_service.get("mongodb.port")
        mongodb_username = config_service.get("mongodb.username")
        mongodb_password = config_service.get("mongodb.password")

        container_service.setup_redis(
            redis_port,
        )

        click.echo(f"Redis server running on port {redis_port}")

        container_service.setup_mongodb(
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
        click.echo("Loading metta file(s)...")
        container_service.setup_canonical_load(
            metta_path,
            canonical,
            mongodb_port=config_service.get("mongodb.port"),
            mongodb_username=config_service.get("mongodb.username"),
            mongodb_password=config_service.get("mongodb.password"),
            redis_port=config_service.get("redis.port"),
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
    container_service.prune()
