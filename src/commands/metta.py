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
from config import USER_DAS_PATH


@click.group()
@click.pass_context
def metta(ctx):
    """
    Manage operations related to the loading of MeTTa files.

    'das-cli metta' allows you to load or just validate the syntax of MeTTa files. Syntax check is a lot faster than actually loading the file so it may be useful to do it before loading very large files.
    """

    global config

    config = ctx.obj["config"]

    try:
        if not config.exists():
            raise FileNotFoundError()

    except FileNotFoundError:
        click.secho(
            f"Configuration file not found in {USER_DAS_PATH}. You can run the command `config set` to create a configuration file.",
            fg="red",
        )
        exit(1)


@metta.command()
@click.argument(
    "path",
    type=click.Path(exists=True),
)
def load(path):
    """
    Load a MeTTa file into the databases.

    'das-cli meta load' loads meta files into the database using the DAS CLI.
    The <path> argument specifies the absolute path (relative paths are not supported) to a MeTTa file to be loaded into the database.
    Depending on the size of the file and the configuration of your server, loading may take a considerable amount of time.
    Before using this command, make sure that the database is running using the 'das-cli db start' command.

    .SH EXAMPLES

    Load a meta file into the database.

    $ das-cli meta load /path/to/mettas-directory/animals.metta
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

    'das-cli metta check' just validates the syntax of a MeTTa file without actually loading it.
    The <path> argument specifies the absolute path (relative paths are not supported) to a MeTTa file.

    .SH EXAMPLES

    Validate the syntax of a MeTTa files.

    $ das-cli metta check /path/to/mettas-directory

    Validate the syntax of a specific metta file.

    $ das-cli metta check /path/to/mettas-directory/animals.metta
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
