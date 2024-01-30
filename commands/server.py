import click
from services.container import ContainerService
from services.config import ConfigService


@click.group()
def server():
    global container_service
    global config

    container_service = ContainerService()
    config = ConfigService()
    config.load()


@server.command()
def configure():
    redis_port = click.prompt(
        "Enter Redis port",
        default=config.get("redis.port", 6379),
        type=int,
    )
    config.set("redis.port", redis_port)

    mongodb_port = click.prompt(
        "Enter MongoDB port",
        default=config.get("mongodb.port", 27017),
        type=int,
    )
    mongodb_username = click.prompt(
        "Enter MongoDB username",
    )
    mongodb_password = click.prompt(
        "Enter MongoDB password",
        hide_input=True,
    )

    config.set("mongodb.port", mongodb_port)
    config.set("mongodb.username", mongodb_username)
    config.set("mongodb.password", mongodb_password)

    config.save()
    click.echo(f"Configuration saved to {config.config_path}")


@server.command()
def start():
    if container_service.is_redis_running() or container_service.is_mongodb_running():
        click.echo("Redis and MongoDB are already running. No further action needed.")
        return

    click.echo("Loading...")

    container_service.setup_redis(
        redis_port=config.get("redis.port"),
    )
    container_service.setup_mongodb(
        mongodb_port=config.get("mongodb.port"),
        mongodb_username=config.get("mongodb.username"),
        mongodb_password=config.get("mongodb.password"),
    )

    click.echo("Done.")


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
    if (
        not container_service.is_redis_running()
        or not container_service.is_mongodb_running()
    ):
        click.echo(
            "Redis or MongoDB is not running. Please use 'server start' to start the required services before running 'server load'."
        )
        return

    click.echo("Loading...")

    container_service.setup_canonical_load(
        metta_path,
        canonical,
        mongodb_port=config.get("mongodb.port"),
        mongodb_username=config.get("mongodb.username"),
        mongodb_password=config.get("mongodb.password"),
        redis_port=config.get("redis.port"),
    )

    click.echo("Done.")


@server.command()
def stop():
    container_service.prune()
