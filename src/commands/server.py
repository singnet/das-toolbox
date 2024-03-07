import click
from sys import exit
from services import (
    RedisContainerService,
    MongoContainerService,
)
from config import Secret, SECRETS_PATH, USER_DAS_PATH
from exceptions import (
    ContainerAlreadyRunningException,
    DockerException,
    NotFound,
    DockerDaemonException,
)


@click.group(help="Manage server-related operations.")
def server():
    """
    This command group allows you to manage server-related operations.
    """

    global config_service

    try:
        config_service = Secret()
    except PermissionError:
        click.secho(
            f"\nWe apologize for the inconvenience, but it seems that you don't have the required permissions to write to {SECRETS_PATH}.\n\nTo resolve this, please make sure you are the owner of the file by running: `sudo chown $USER:$USER {USER_DAS_PATH} -R`, and then grant the necessary permissions using: `sudo chmod 770 {USER_DAS_PATH} -R`\n",
            fg="red",
        )
        exit(1)


@server.command(help="Start Redis and MongoDB containers.")
def start():
    """
    Start Redis and MongoDB containers.
    """

    click.echo("Starting Redis and MongoDB...")

    redis_container_name = config_service.get("redis.container_name")
    redis_port = config_service.get("redis.port")


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

    mongodb_container_name = config_service.get("mongodb.container_name")
    mongodb_port = config_service.get("mongodb.port")
    mongodb_username = config_service.get("mongodb.username")
    mongodb_password = config_service.get("mongodb.password")


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


@server.command(help="Stop and remove all currently running services.")
def stop():
    """
    Stop and remove all currently running services.
    """

    click.echo(f"Stopping redis service...")

    redis_container_name = config_service.get("redis.container_name")

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

    mongodb_container_name = config_service.get("mongodb.container_name")

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
