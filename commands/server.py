import click
from services.container import (
    RedisContainerService,
    MongoContainerService,
    CanonicalLoadContainerService,
    OpenFaaSContainerService,
)
from sys import exit
from config import Config


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
    click.echo("Starting Redis and MongoDB...")

    redis_service = RedisContainerService()

    redis_port = config.get("redis.port")
    mongodb_port = config.get("mongodb.port")
    mongodb_username = config.get("mongodb.username")
    mongodb_password = config.get("mongodb.password")

    if redis_service.get_container().container_running():
        click.echo(f"Redis is already running. It's listening on port {redis_port}")
    else:
        try:
            redis_service.start_container(
                redis_port,
            )
            click.echo(f"Redis started on port {redis_port}")
        except Exception as e:
            click.echo(
                f"Error occurred while trying to start Redis on port {redis_port}"
            )
            click.echo(f"Error Details: {str(e)}")
            click.echo(
                f"For more information, check the logs using the command 'docker logs das-redis' in your terminal."
            )
            exit(1)

    mongodb_service = MongoContainerService()

    if mongodb_service.get_container().container_running():
        click.echo(f"MongoDB is already running. It's listening on port {mongodb_port}")
    else:
        try:
            mongodb_service.start_container(
                mongodb_port,
                mongodb_username,
                mongodb_password,
            )

            click.echo(f"MongoDB started on port {mongodb_port}")
        except Exception as e:
            click.echo(
                f"Error occurred while trying to start MongoDB on port {mongodb_port}"
            )
            click.echo(f"Error Details: {str(e)}")
            click.echo(
                f"For more information, check the logs using the command 'docker logs das-mongodb' in your terminal."
            )
            exit(1)

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
            metta_path,
            canonical,
            mongodb_port=config.get("mongodb.port"),
            mongodb_username=config.get("mongodb.username"),
            mongodb_password=config.get("mongodb.password"),
            redis_port=config.get("redis.port"),
        )
        click.echo("Done.")
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
