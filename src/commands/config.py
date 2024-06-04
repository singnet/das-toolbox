import click
from config import SECRETS_PATH, USER_DAS_PATH, Secret as Config
from utils import table_parser, get_server_username, get_public_ip
from sys import exit
from enums import FunctionEnum
from services import ContainerRemoteService
from typing import List, Dict


@click.group()
@click.pass_context
def config(ctx):
    """
    'das-cli config' allows you to manage configuration settings for the DAS CLI, with commands to set, list, and modify
    parameters such as port numbers, usernames and other configuration settings required by various DAS components.
    """

    global config_service

    config_service = ctx.obj["config"]


def _set_redis_nodes(cluster_nodes: List[Dict], min_servers: int = 3):
    add_more_nodes_flag = True
    servers = []

    while True:
        if add_more_nodes_flag == False:
            break

        server_ip = click.prompt(
            "Enter the server ip address",
            hide_input=False,
        )
        # TODO: validate if it's a valid ip

        server_username = click.prompt(
            "Enter the server username",
            hide_input=False,
        )

        servers.append(
            {
                "ip": server_ip,
                "username": server_username,
            }
        )

        if len(servers) >= min_servers - 1:
            add_more_nodes_flag = click.prompt(
                "Do you want to add more servers? (yes/no)",
                hide_input=False,
                type=bool,
            )

    container_remote_service = ContainerRemoteService(servers)

    cluster_nodes += container_remote_service.create_context()


def _remove_redis_contexts(config_service: Config):
    nodes = config_service.get("redis.nodes")

    container_remote_service = ContainerRemoteService(nodes)

    container_remote_service.remove_context()


def _set_redis(config_service: Config):
    redis_port = click.prompt(
        "Enter Redis port",
        default=config_service.get("redis.port", 6379),
        type=int,
    )
    config_service.set("redis.port", redis_port)

    redis_container_name = f"das-cli-redis-{redis_port}"
    config_service.set("redis.container_name", redis_container_name)

    cluster_default_value = "yes" if config_service.get("redis.cluster") else "no"

    redis_cluster = click.prompt(
        "Is it a redis cluster? (yes/no) ",
        hide_input=False,
        default=cluster_default_value,
        type=bool,
    )
    config_service.set("redis.cluster", redis_cluster)

    nodes = []
    server_user = get_server_username()
    redis_current_node = {
        "context": "default",
        "ip": "localhost",
        "username": server_user,
    }

    if redis_cluster:
        server_public_ip = get_public_ip()

        if server_public_ip is None:
            raise Exception(
                "The server's public ip could not be solved. Make sure it has internet access."
            )

        redis_current_node["ip"] = server_public_ip

        _set_redis_nodes(nodes)

    nodes.insert(0, redis_current_node)

    _remove_redis_contexts(config_service)

    config_service.set("redis.nodes", nodes)


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
    This file contains several variables that influence the behavior of DAS commands based on the user's provided parameters.

    .SH EXAMPLES

    Set configuration settings for the DAS CLI.

    $ das-cli config set

    .sh VARIABLES

    redis.*
        These variables control Redis settings, such as:

        redis.port
            Defines the port number on which the Redis server is listening. The user must ensure this port is available on the server where das-cli is running and also on other nodes if a cluster is being used. If using a firewall like `ufw`, the user can allow the necessary ports for cluster communication using the command `ufw allow 7000:17000/tcp` to ensure proper communication within the cluster, assuming the Redis instance operates on port 7000. It's recommended to restrict access to specific IP addresses for each node. This practice enhances security and minimizes potential vulnerabilities.

        redis.container_name
            Specifies the name of the Docker container running the Redis server.

        redis.custer
            Indicates whether a Redis cluster is being used (true/false).

        redis.nodes
            Receives a list of nodes for Redis configuration. For a single-node setup, there must be at least one node specified with the default context. For a cluster setup, there must be at least three nodes specified. Additionally, it is necessary to configure an SSH key and utilize this key on each node to ensure SSH connectivity between them. This is essential because Docker communicates between nodes remotely to deploy images with Redis. To establish SSH connectivity, generate an SSH key using `ssh-keygen` and add this key to all servers in the cluster. Ensure that port 22 is open on all servers to allow SSH connections.

        redis.nodes.[].context
            The name of the Docker context containing connection information for the remote Docker instances of other nodes.

        redis.nodes.[].ip
            The IP address of the node.

        redis.nodes.[].username
            The username for connecting to the node.

    mongodb.*
        These variables control MongoDB settings, such as:

        mongodb.port
            Defines the port number on which the MongoDB server is listening. The user must ensure this port is available on the server where das-cli is running.

        mongodb.container_name
            Specifies the name of the Docker container running the MongoDB server.

        mongodb.username
            The username for connecting to the MongoDB server.

        mongodb.password
            The password for connecting to the MongoDB server.

    loader.*
        These variables control the Loader settings, responsible for validating and loading meta files into the database, such as:

        loader.container_name
            Specifies the name of the Docker container running the Loader.

    openfaas.*
        These variables control OpenFaaS settings, such as:

        openfaas.container_name
            Specifies the name of the Docker container running OpenFaaS.

        openfaas.version
            Specifies the version of OpenFaaS function being used.

        openfaas.function
            Specifies the name of the function to be executed within OpenFaaS.

    jupyter_notebook.*
        These variables control Jupyter Notebook settings, such as:

        jupyter_notebook.port
            Defines the port number on which the Jupyter Notebook server is listening.

        jupyter_notebook.container_name
            Specifies the name of the Docker container running the Jupyter Notebook server.

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
