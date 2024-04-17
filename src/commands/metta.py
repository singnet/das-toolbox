import os
import click
from sys import exit
from services import MettaLoaderContainerService
from services import MettaSyntaxValidatorService
from exceptions import (
    DockerException,
    ContainerNotRunningException,
    DockerDaemonException,
    MettaLoadException,
)


@click.group()
@click.pass_context
def metta(ctx):
    """
    Manage Metta operations.

    This command group enables you to manage Metta operations, such as validating the syntax of Metta files and loading them into databases.
    """

    global config

    config = ctx.obj["config"]


@metta.command()
@click.argument(
    "path",
    type=click.Path(exists=True),
)
def load(path):
    """
    Load a MeTTa file into the databases.

    The \\fBdas-cli meta load\\fR command loads meta files into the database using the DAS CLI.
    The <path> argument specifies the absolute path to a meta file to be loaded into the database.
    Depending on the size of the file and the configuration of your server, loading may take a considerable amount of time.
    Before using this command, ensure that the database is running using the \\fBdas-cli db start\\fR command.

    .SH EXAMPLES

    Load a meta file into the database.

    \\fB$ das-cli meta load /path/to/mettas-directory/animals.metta\\fR
    """

    loader_container_name = config.get("loader.container_name")
    redis_container_name = config.get("redis.container_name")
    mongodb_container_name = config.get("mongodb.container_name")
    services_not_running = False

    try:
        loader_service = MettaLoaderContainerService(
            loader_container_name,
            redis_container_name,
            mongodb_container_name,
        )

        if not loader_service.redis_container.is_running():
            click.secho("Redis is not running", fg="red")
            services_not_running = True
        else:
            click.secho(
                f"Redis is running on port {config.get('redis.port')}",
                fg="yellow",
            )

        if not loader_service.mongodb_container.is_running():
            click.secho("MongoDB is not running", fg="red")
            services_not_running = True
        else:
            click.secho(
                f"MongoDB is running on port {config.get('mongodb.port')}",
                fg="yellow",
            )

        if services_not_running:
            raise ContainerNotRunningException(
                "\nPlease use 'db start' to start required services before running 'metta load'."
            )

        click.echo("Loading metta file(s)...")

        loader_service.start_container(
            path,
            mongodb_port=config.get("mongodb.port"),
            mongodb_username=config.get("mongodb.username"),
            mongodb_password=config.get("mongodb.password"),
            redis_port=config.get("redis.port"),
        )
        click.echo("Done.")
    except (
        DockerDaemonException,
        DockerException,
        ContainerNotRunningException,
        FileNotFoundError,
        IsADirectoryError,
        MettaLoadException,
    ) as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)


@metta.command()
@click.argument(
    "path",
    type=click.Path(exists=True),
)
def check(path: str):
    """
    Validate syntax of MeTTa files used with the DAS CLI

    The \\fBdas-cli metta check\\fR command validates the syntax of MeTTa files that eventually will be loaded into the database using the \\fBdas-cli metta load\\fR command.
    The <path> argument specifies the absolute path to either a directory containing metta files or a specific metta file.

    .SH EXAMPLES

    Validate the syntax of MeTTa files located in the specified directory.

    \\fB$ das-cli metta check /path/to/mettas-directory\\fR

    Validate the syntax of a specific metta file.

    \\fB$ das-cli metta check /path/to/mettas-directory/animals.metta\\fR
    """

    try:
        metta_service = MettaSyntaxValidatorService()

        if os.path.isdir(path):
            metta_service.validate_directory(
                path,
            )
        else:
            metta_service.validate_file(path)
    except Exception as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)
