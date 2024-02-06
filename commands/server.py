import click
from services.container import (
    RedisContainerService,
    MongoContainerService,
    CanonicalLoadContainerService,
    OpenFaaSContainerService,
)
from sys import exit
from config import Config


@click.group(help="Manage server-related operations.")
def server():
    """
    This command group allows you to manage server-related operations.
    """

    global config

    config = Config()

    if not config.exists():
        click.echo(
            "The configuration file does not exist. Please initialize the configuration file first by running the command config set."
        )
        exit(1)


@server.command(help="Start Redis and MongoDB containers.")
def start():
    """
    Start Redis and MongoDB containers.
    """

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


@server.command(help="Stop and remove all currently running services.")
def stop():
    """
    Stop and remove all currently running services.
    """

    click.echo(f"Stopping/Removing Currently Running Services")
    OpenFaaSContainerService().stop()
    CanonicalLoadContainerService().stop()
    MongoContainerService().stop()
    RedisContainerService().stop()
    click.echo(f"Done.")
