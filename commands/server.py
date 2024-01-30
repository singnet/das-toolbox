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
    container_service.setup_redis(
        redis_port=config.get("redis.port"),
    )
    container_service.setup_mongodb(
        mongodb_port=config.get("mongodb.port"),
        mongodb_username=config.get("mongodb.username"),
        mongodb_password=config.get("mongodb.password"),
    )


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
    container_service.setup_canonical_load(
        metta_path,
        canonical,
        mongodb_port=config.get("mongodb.port"),
        mongodb_username=config.get("mongodb.username"),
        mongodb_password=config.get("mongodb.password"),
        redis_port=config.get("redis.port"),
    )


@server.command()
def stop():
    container_service.prune()
