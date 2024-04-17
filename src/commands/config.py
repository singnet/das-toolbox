import click
from config import SECRETS_PATH, USER_DAS_PATH
from utils import table_parser
from sys import exit


@click.group()
@click.pass_context
def config(ctx):
    """
    The das-cli config command allows you to manage configuration settings for the DAS CLI.
    This tool provides commands to set, list, and modify configuration settings, such as port numbers, usernames, and other parameters required by various DAS components.
    """

    global config_service

    config_service = ctx.obj["config"]


@config.command()
def set():
    """
    Set configuration settings for the DAS CLI

    The \\fBdas-cli config set\\fR command prompts the user to set configuration settings for the DAS CLI.
    These settings include parameters such as port numbers, usernames, and other relevant information required by various DAS components.
    The command displays prompts for each configuration option, suggesting default values if available.
    If the user has already configured a setting, the default value will be the previously set value, allowing for quick modifications.
    Once all configurations are provided, the command will also inform the user about the location where the configuration file was created.

    .SH EXAMPLES

    Set configuration settings for the DAS CLI.

    \\fB$ das-cli config set\\fR

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

        openfaas_function = f"queryengine"
        config_service.set("openfaas.function", openfaas_function)

        jupyter_notebook_port = click.prompt(
            "Enter Jupyter Notebook port",
            hide_input=True,
            default=config_service.get("jupyter.port", 8888),
        )
        config_service.set("jupyter_notebook.port", jupyter_notebook_port)

        jupyter_notebook_container_name = (
            f"das-cli-jupyter-notebook-{jupyter_notebook_port}"
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


@config.command()
def list():
    """
    Display the current configuration settings.

    The das-cli config list command displays the user-defined configurations set using the \\fBdas-cli config set\\fR command.
    The command outputs the configurations in a table format, providing a user-friendly overview of the settings.

    .SH EXAMPLES

    Display the configuration settings

    \\fB$ das-cli config list\\fR
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
