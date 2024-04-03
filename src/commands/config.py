import click
from config import SECRETS_PATH, USER_DAS_PATH
from utils import table_parser
from sys import exit


@click.group(help="Manage configuration settings.")
@click.pass_context
def config(ctx):
    """
    This command group allows you to manage configuration settings.
    """

    global config_service

    config_service = ctx.obj["config"]


@config.command(help="Set Redis and MongoDB configuration settings.")
def set():
    """
    Set Redis and MongoDB configuration settings.
    """

    try:
        redis_port = click.prompt(
            "Enter Redis port",
            default=config_service.get("redis.port", 6379),
            type=int,
        )
        config_service.set("redis.port", redis_port)

        redis_container_name = f"das-cli-redis-{redis_port}"
        config_service.set("redis.container_name", redis_container_name)

        mongodb_port = click.prompt(
            "Enter MongoDB port",
            default=config_service.get("mongodb.port", 27017),
            type=int,
        )
        config_service.set("mongodb.port", mongodb_port)

        mongodb_container_name = f"das-cli-mongodb-{mongodb_port}"
        config_service.set("mongodb.container_name", mongodb_container_name)

        mongodb_username = click.prompt(
            "Enter MongoDB username",
            default=config_service.get("mongodb.username", "admin"),
        )
        config_service.set("mongodb.username", mongodb_username)
        mongodb_password = click.prompt(
            "Enter MongoDB password",
            hide_input=True,
            default=config_service.get("mongodb.password", "admin"),
        )
        config_service.set("mongodb.password", mongodb_password)

        loader_container_name = "das-cli-loader"
        config_service.set("loader.container_name", loader_container_name)

        openfaas_container_name = f"das-cli-openfaas-8080"
        config_service.set("openfaas.container_name", openfaas_container_name)

        openfaas_version = f"latest"
        config_service.set("openfaas.version", openfaas_version)

        jupyter_notebook_port = click.prompt(
            "Enter Jupyter Notebook port",
            hide_input=True,
            default=config_service.get("jupyter.port", 8888),
        )
        config_service.set("jupyter_notebook.port", jupyter_notebook_port)

        jupyter_notebook_container_name = (
            f"das-jupyter-notebook-{jupyter_notebook_port}"
        )
        config_service.set(
            "jupyter_notebook.container_name",
            jupyter_notebook_container_name,
        )

        config_service.save()

        click.secho(
            f"Configuration file saved -> {SECRETS_PATH}",
            fg="green",
        )
    except PermissionError:
        click.secho(
            f"\nIt seems that you don't have the required permissions to write to {SECRETS_PATH}.\n\nTo resolve this, please make sure you are the owner of the file by running: `sudo chown $USER:$USER {USER_DAS_PATH} -R`, and then grant the necessary permissions using: `sudo chmod 770 {USER_DAS_PATH} -R`\n",
            fg="red",
        )
        exit(1)


@config.command(help="Display the current configuration settings.")
def list():
    """
    Display the current configuration settings.
    """

    try:
        config_dict = config_service.get_content()

        if len(config_dict.keys()) < 1:
            raise FileNotFoundError()

        config_table = table_parser(config_dict)

        click.echo(config_table)
    except PermissionError:
        click.secho(
            f"\nIt seems that you don't have the required permissions to write to {SECRETS_PATH}.\n\nTo resolve this, please make sure you are the owner of the file by running: `sudo chown $USER:$USER {USER_DAS_PATH} -R`, and then grant the necessary permissions using: `sudo chmod 770 {USER_DAS_PATH} -R`\n",
            fg="red",
        )
        exit(1)
    except FileNotFoundError:
        click.secho(
            f"Configuration file not found in {USER_DAS_PATH}. You can run the command `config set` to create a configuration file.",
            fg="red",
        )
        exit(1)
