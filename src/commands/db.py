import click
from sys import exit
from services import (
    RedisContainerService,
    MongoContainerService,
)
from exceptions import (
    ContainerAlreadyRunningException,
    DockerException,
    NotFound,
    DockerDaemonException,
)


@click.group(help="Manage db-related operations.")
@click.pass_context
def db(ctx):
    """
    This command group allows you to manage db-related operations.
    """

    global config

    config = ctx.obj["config"]


@db.command(help="Start Redis and MongoDB containers.")
def start():
    """
    Start Redis and MongoDB containers.
    """

    click.echo("Starting Redis and MongoDB...")

    redis_container_name = config.get("redis.container_name")
    redis_port = config.get("redis.port")

    try:
        redis_service = RedisContainerService(redis_container_name)

        redis_service.start_container(
            redis_port,
        )
        click.secho(f"Redis started on port {redis_port}", fg="green")
    except ContainerAlreadyRunningException:
        click.secho(
            f"Redis is already running. It's listening on port {redis_port}",
            fg="yellow",
        )
    except (DockerException, DockerDaemonException) as e:
        click.secho(
            f"\nError occurred while trying to start Redis on port {redis_port}\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)

    mongodb_container_name = config.get("mongodb.container_name")
    mongodb_port = config.get("mongodb.port")
    mongodb_username = config.get("mongodb.username")
    mongodb_password = config.get("mongodb.password")

    try:
        mongodb_service = MongoContainerService(mongodb_container_name)

        mongodb_service.start_container(
            mongodb_port,
            mongodb_username,
            mongodb_password,
        )
        click.secho(f"MongoDB started on port {mongodb_port}", fg="green")

    except ContainerAlreadyRunningException:
        click.secho(
            f"MongoDB is already running. It's listening on port {mongodb_port}",
            fg="yellow",
        )
    except (DockerException, DockerDaemonException) as e:
        click.secho(
            f"\nError occurred while trying to start MongoDB on port {mongodb_port}\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)

    click.echo("Done.")


@db.command(help="Stop and remove all currently running services.")
def stop():
    """
    Stop and remove all currently running services.
    """

    click.echo(f"Stopping redis service...")

    redis_container_name = config.get("redis.container_name")

    try:
        RedisContainerService(redis_container_name).stop()
        click.secho("Redis service stopped", fg="green")
    except NotFound:
        click.secho(
            f"The Redis service named {redis_container_name} is already stopped.",
            fg="yellow",
        )
    except DockerException as e:
        click.secho(
            f"\nError occurred while trying to stop Redis\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)

    mongodb_container_name = config.get("mongodb.container_name")

    try:
        MongoContainerService(mongodb_container_name).stop()
        click.secho("MongoDB service stopped", fg="green")
    except NotFound:
        click.secho(
            f"The MongoDB service named {mongodb_container_name} is already stopped.",
            fg="yellow",
        )
    except DockerException as e:
        click.secho(
            f"\nError occurred while trying to stop MongoDB\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)

    click.echo(f"Done.")
