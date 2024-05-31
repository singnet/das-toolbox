import click
from time import sleep
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


@click.group()
@click.pass_context
def db(ctx):
    """
    Manage db-related operations.

    'das-cli db' commands allow you to manage DAS backend DBMSs for use with the DAS CLI. 'das-cli db' provides commands to start, stop, and restart the databases as needed.
    """

    global config

    config = ctx.obj["config"]


@db.command()
def restart():
    """
    Restart all DBMS containers.

    'das-cli db restart' restarts all database containers previously started with 'das-cli start'. If no database have been started, 'das-cli db restart' just start them.

    IMPORTANTE NOTE: Restarting the databases will result in all data being lost. Databases are started empty.

    .SH EXAMPLES

    Restart DBMS containers previously started with the 'das-cli db start'.

    $ das-cli db restart
    """
    ctx = click.Context(restart)
    ctx.invoke(stop)
    ctx.invoke(start)


def _start_redis():
    redis_container_name = config.get("redis.container_name")
    redis_port = config.get("redis.port")
    redis_nodes = config.get("redis.nodes")

    try:
        for node_context in redis_nodes:
            redis_service = RedisContainerService(
                redis_container_name,
                exec_context=node_context,
            )

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


def _start_mongodb():
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


@db.command()
def start():
    """
    Starts all DBMS containers.

    'das-cli db start' initiates all databases.
    These databases can either be utilized alongside DAS FaaS Function or connected directly to a local DAS instance.

    Upon execution, the command will display the ports on which each database is running.
    Note that the port configuration can be modified using the 'das-cli config set' command.

    .SH EXAMPLES

    Start all databases for use with the DAS.

    $ das-cli db start
    """

    click.echo("Starting Redis and MongoDB...")

    _start_redis()
    _start_mongodb()

    click.echo("Done.")


@db.command()
def stop():
    """
    Stops all DBMS containers.

    'das-cli db stop' stops the DBMS containers that were previously started with the 'das-cli db start'.
    This command is useful for shutting down the databases when they are no longer needed.

    IMPORTANT NOTE: After stopping the databases, all data will be lost.

    .SH EXAMPLES

    Stop DBMS containers previously started with 'das-cli db start'.

    $ das-cli db stop
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

    sleep(10)
    click.echo(f"Done.")
