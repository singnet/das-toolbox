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

    The \\fBdas-cli db\\fR command allows you to manage MongoDB and Redis databases for use with the DAS CLI. This tool provides commands to start, stop, and restart the databases as needed.
    """

    global config

    config = ctx.obj["config"]


@db.command()
def restart():
    """
    Restart Redis and MongoDB containers.

    The \\fBdas-cli db restart\\fR command restarts the MongoDB and Redis databases that were previously started with the DAS CLI.
    This command is useful for restarting the databases to apply changes or address issues.

    \\fBNote:\\fR Restarting the databases will result in all data being lost.
    When the databases are started again, they will be empty.
    You will need to use the \\fBdas-cli meta load\\fR command to reload the data.

    .SH EXAMPLES

    Restart MongoDB and Redis databases previously started with the DAS CLI.

    \\fB$ das-cli db restart\\fR
    """
    ctx = click.Context(restart)
    ctx.invoke(stop)
    ctx.invoke(start)


@db.command()
def start():
    """
    Start Redis and MongoDB databases.

    The \\fBdas-cli db start\\fR command initiates MongoDB and Redis databases.
    These databases can either be utilized alongside DAS FaaS Function or connected directly to a local DAS instance.

    Upon execution, the command will display the ports on which MongoDB and Redis are running.
    Note that the port configuration can be modified using the \\fBdas-cli config set\\fR command.

    .SH EXAMPLES

    Start MongoDB and Redis databases for use with the DAS CLI.

    \\fB$ das-cli db start\\fR
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


@db.command()
def stop():
    """
    Stop Redis and MongoDB databases.

    The \\fBdas-cli db stop\\fR command stops the MongoDB and Redis databases that were previously started with the DAS CLI.
    This command is useful for shutting down the databases when they are no longer needed.

    \\fBNote:\\fR After stopping the databases, all data will be lost. When starting the databases again, they will be empty.
    You will need to use the \\fBdas-cli meta load\\fR command to reload the data.

    .SH EXAMPLES

    Stop MongoDB and Redis databases previously started with the DAS CLI.

    \\fB$ das-cli db stop\\fR
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
