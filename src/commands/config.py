import click
from config import SECRETS_PATH, USER_DAS_PATH, Secret as Config
from utils import table_parser, get_public_ip, get_server_username
from sys import exit
from enums import FunctionEnum
from services import ContainerRemoteService


@click.group()
@click.pass_context
def config(ctx):
    """
    'das-cli config' allows you to manage configuration settings for the DAS CLI, with commands to set, list, and modify
    parameters such as port numbers, usernames and other configuration settings required by various DAS components.
    """

    global config_service

    config_service = ctx.obj["config"]


def _set_redis_cluster(config_service: Config):
    server_public_ip = "127.0.0.1"
    server_user = get_server_username()

    min_nodes = 3
    nodes = []
    add_more_nodes_flag = True

    if server_public_ip is None:
        raise Exception(
            "The server's public ip could not be solved. Make sure it has internet access."
        )
    else:
        nodes.append(
            {
                "ip": server_public_ip,
                "username": server_user,
            }
        )

    while True:
        if add_more_nodes_flag == False:
            break

        node_ip = click.prompt(
            "Enter the server ip address",
            hide_input=False,
        )
        # TODO: validate if it's a valid ip

        node_username = click.prompt(
            "Enter the server username",
            hide_input=False,
        )

        nodes.append(
            {
                "ip": node_ip,
                "username": node_username,
            }
        )

        if len(nodes) >= min_nodes:
            add_more_nodes_flag = click.prompt(
                "Do you want to add more nodes? (yes/no)", hide_input=False, type=bool
            )

    container_remote_service = ContainerRemoteService(nodes)

    servers_context = container_remote_service.create_context()
    config_service.set("redis.nodes", servers_context)


def _set_redis(config_service: Config):
    redis_port = click.prompt(
        "Enter Redis port",
        default=config_service.get("redis.port", 6379),
        type=int,
    )
    config_service.set("redis.port", redis_port)

    redis_container_name = f"das-cli-redis-{redis_port}"
    config_service.set("redis.container_name", redis_container_name)

    redis_cluster = click.prompt(
        "Is it a redis cluster? (yes/no) ",
        hide_input=False,
        default=config_service.get("redis.cluster"),
        type=bool,
    )
    config_service.set("redis.cluster", redis_cluster)

    if redis_cluster:
        _set_redis_cluster(config_service)


def _set_mongodb(config_service: Config):
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


def _set_loader(config_service: Config):
    loader_container_name = "das-cli-loader"
    config_service.set("loader.container_name", loader_container_name)


def _set_openfaas(config_service: Config):
    openfaas_container_name = f"das-cli-openfaas-8080"
    config_service.set("openfaas.container_name", openfaas_container_name)
    openfaas_version = f"latest"
    config_service.set("openfaas.version", openfaas_version)
    config_service.set("openfaas.function", FunctionEnum.QUERY_ENGINE.value)


def _set_jupyter_notebook(config_service: Config):
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


@config.command()
def set():
    """

    'das-cli config set' Sets configuration parameters for DAS CLI.

    'das-cli config set' prompts the user for configuration settings for the DAS CLI.
    These settings include parameters such as port numbers, usernames, and other relevant information required by various DAS components.
    The command displays prompts for each configuration option, suggesting default values when available.
    If the user has already configured a setting, the default value will be the previously set value, allowing for quick modifications.
    Once all configurations are provided, the command will also inform the user about the location where the configuration file was created.

    .SH EXAMPLES

    Set configuration settings for the DAS CLI.

    $ das-cli config set

    """

    try:
        _set_redis(config_service)
        _set_mongodb(config_service)
        _set_loader(config_service)
        _set_openfaas(config_service)
        _set_jupyter_notebook(config_service)

        config_service.save()

        click.secho(
            f"Configuration file saved -> {SECRETS_PATH}",
            fg="green",
        )
    except PermissionError:
        click.secho(
            f"\nPermission denied trying to write to {SECRETS_PATH}.",
            fg="red",
        )
        exit(1)
    except Exception as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)


@config.command()
def list():
    """
    'das-cli config list' displays current configuration settings.

    .SH EXAMPLES

    Display current configuration settings

    $ das-cli config list
    """

    try:
        config_dict = config_service.get_content()

        if len(config_dict.keys()) < 1:
            raise FileNotFoundError()

        config_table = table_parser(config_dict)

        click.echo(config_table)
    except PermissionError:
        click.secho(
            f"\nPermission denied trying to write to {SECRETS_PATH}.",
            fg="red",
        )
        exit(1)
    except FileNotFoundError:
        click.secho(
            f"Configuration file not found in {USER_DAS_PATH}. You can run the command `config set` to create a configuration file.",
            fg="red",
        )
        exit(1)
