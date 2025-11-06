from typing import Optional

from injector import inject

from common import (
    Command,
    CommandArgument,
    CommandGroup,
    CommandOption,
    KeyValueType,
    RemoteContextManager,
    Settings,
    StdoutSeverity,
    StdoutType,
)
from common.config.loader import CompositeLoader, EnvFileLoader, EnvVarLoader
from common.prompt_types import AbsolutePath

from .config_provider import InteractiveConfigProvider, NonInteractiveConfigProvider


class ConfigSet(Command):
    name = "set"

    short_help = "Interactively set DAS CLI configuration parameters."

    help = """
NAME
    das-cli config set - Interactively set configuration parameters for the DAS CLI.

SYNOPSIS
    das-cli config set


DESCRIPTION
    The 'config set' command prompts the user to configure various DAS CLI components,
    such as ports, container names, and cluster settings.

    For each configuration option, a prompt is displayed with a suggested default value
    (if available). If a value has been set previously, it is shown as the default.

SECTIONS

    ┌────────────────────┐
    │ 1. schema_hash     │
    | 2. AtomDB Backend  │
    │ 3. Redis           │
    │ 4. MongoDB         │
    | 5. MorkDB          │
    │ 6. Loader          │
    │ 7. Jupyter         │
    │ 8. DAS Peer        │
    │ 9. DBMS Peer       │
    │ 10. AttentionBroker│
    │ 11. Query Agent    │
    │ 12. Link Agent     │
    │ 13. Evolution Agent│
    │ 14. Context Broker │
    └────────────────────┘

OPTIONS AND VARIABLES

SCHEMA HASH CONFIGURATION (schema_hash)

    This variable stores the hash of the schema file used by DAS CLI. It is used to verify the integrity of the schema file and ensure that the correct version is being used.
    After completion, the path to the generated configuration file will be shown. This file
    governs how DAS commands interact with services such as Redis, MongoDB, OpenFaaS, etc.


SERVICES CONFIGURATION (services.*)

    ATOMDB BACKEND CONFIGURATION (database.atomdb_backend)

        database.atomdb_backend
            Defines the backend used for AtomDB storage. Supported options are:
            - redis_mongodb: Uses Redis for caching and MongoDB for persistent storage.
            - mork_mongodb: Uses MorkDB for caching and MongoDB for persistent storage

    REDIS CONFIGURATION (redis.*)

        redis.port
            Defines the port number on which the Redis server is listening.
            The user must ensure this port is available on the server where das-cli
            is running and also on other nodes if a cluster is being used.

            If using a firewall like `ufw`, the user can allow the necessary ports
            for cluster communication using the commands below, assuming the Redis
            instance operates on port 7000:

                sudo ufw allow 7000/tcp
                sudo ufw allow 17000/tcp

            The cluster bus uses port 10000 + redis.port, so for a Redis instance
            running on port 7000, port 17000 must also be allowed.

            It is recommended to restrict access to specific IP addresses for each
            node. This practice enhances security and minimizes potential vulnerabilities.

        redis.container_name
            Specifies the name of the Docker container running the Redis server.

        redis.cluster
            Indicates whether a Redis cluster is being used (true/false).

            To allow cluster setup and communication, passwordless SSH access must be configured:

            - Generate an RSA key (on the first machine only):

                ssh-keygen

            Leave the password empty when prompted.

            - Distribute the public key (~/.ssh/id_rsa.pub) to all other machines
            in the cluster by adding it to their ~/.ssh/authorized_keys files.

            This allows the first machine to SSH into all others without a
            password, which is necessary for automated Redis cluster initialization.

            All machines participating in the Redis cluster must:

            - Use the default Docker context:

                docker context use default

            - Ensure that the current user has permission to run Docker commands
            (e.g., is part of the `docker` group):

                sudo usermod -aG docker $USER

        redis.nodes
            List of Redis nodes. Minimum 1 node (standalone), 3 nodes (cluster).
            Additionally, it is necessary to configure an SSH key and utilize this key on each node to ensure SSH connectivity between them.
            This is essential because Docker communicates between nodes remotely to deploy images with Redis.
            To establish SSH connectivity, generate an SSH key using `ssh-keygen` and add this key to all servers in the cluster.
            Ensure that port 22 is open on all servers to allow SSH connections.

        redis.nodes.[].context
            The name of the Docker context containing connection information for the remote Docker instances of other nodes.

        redis.nodes.[].ip
            IP address of the node.

        redis.nodes.[].username
            SSH username to connect to the node.

    MONGODB CONFIGURATION (mongodb.*)

        mongodb.port
            Port where the MongoDB server listens.
            The user must ensure this port is available on the server where das-cli is running.

        mongodb.container_name
            Specifies the name of the Docker container running the MongoDB server.

        mongodb.username
            The username for connecting to the MongoDB server.

        mongodb.password
            The password for connecting to the MongoDB server.

        mongodb.cluster
            Enable MongoDB clustering (true/false).

        mongodb.cluster_secret_key
            Secret key shared among cluster nodes for authentication.

        mongodb.nodes
            List of MongoDB nodes. Minimum 1 node (standalone), 3 nodes (cluster).
            Additionally, it is necessary to configure an SSH key and utilize this key on each node to ensure SSH connectivity between them.
            This is essential because Docker communicates between nodes remotely to deploy images with MongoDB. To establish SSH connectivity, generate an SSH key using `ssh-keygen` and add this key to all servers in the cluster.
            Ensure that port 22 is open on all servers to allow SSH connections.

        mongodb.nodes.[].context
            The name of the Docker context containing connection information for the remote Docker instances of other nodes.

        mongodb.nodes.[].ip
            IP address of the node.

        mongodb.nodes.[].username
            SSH username to connect to the node.

    MORKDB CONFIGURATION (morkdb.*)
        morkdb.port
            Port where the MorkDB server listens.
            The user must ensure this port is available on the server where das-cli is running.

        morkdb.container_name
            Specifies the name of the Docker container running the MorkDB server.

    LOADER CONFIGURATION (loader.*)

        loader.container_name
            Specifies the name of the Docker container running the Loader.

    JUPYTER NOTEBOOK CONFIGURATION (jupyter_notebook.*)

        jupyter_notebook.port
            Port where the Jupyter Notebook server listens.

        jupyter_notebook.container_name
            specifies the name of the Docker container running the Jupyter Notebook server.

    DAS PEER CONFIGURATION (das_peer.*)

        das_peer.container_name
            Specifies the Docker container name for the DAS peer, which acts as the main server. This name is essential for managing and communicating with the DAS peer container.

    DBMS PEER CONFIGURATION (dbms_peer.*)

        dbms_peer.container_name
            Specifies the Docker container name for the DBMS peer, which connects to the DAS peer to send data.

    ATTENTION BROKER CONFIGURATION (attention_broker.*)

        attention_broker.port
            Listening port for the Attention Broker.
            The user must ensure this port is available on the server where DAS is running.

        attention_broker.container_name
            Specifies the name of the Docker container running the Attention Broker.

    QUERY AGENT CONFIGURATION (query_agent.*)

        query_agent.port
            Listening port for the Query Agent.
            The user must ensure this port is available on the server.

        query_agent.container_name
            Specifies the name of the Docker container running the Query Agent.

    LINK CREATION AGENT CONFIGURATION (link_creation_agent.*)

        link_creation_agent.port
            Listening port for the Link Creation Agent.

        link_creation_agent.container_name
            Specifies the name of the Docker container running the Link Creation Agent.

    EVOLUTION AGENT CONFIGURATION (evolution.*)

        evolution.port
            Listening port for the Evolution.
            The user must ensure this port is available on the server.

        evolution.container_name
            Specifies the name of the Docker container running the Evolution.

    CONTEXT BROKER CONFIGURATION (context_broker.*)

        context_broker.port
            Listening port for the Context Broker.
            The user must ensure this port is available on the server.

        context_broker.container_name
            Specifies the name of the Docker container running the Context Broker.


EXAMPLES

    Set all configuration options interactively:
        $ das-cli config set


"""

    params = [
        CommandOption(
            ["--from-env"],
            help="Path to an environment file to load initial configuration values from to be suggested as the default value in the interactive prompts.",
            required=False,
            type=AbsolutePath(
                file_okay=True,
                dir_okay=False,
                exists=True,
                writable=True,
                readable=True,
            ),
        ),
        CommandArgument(
            ["config_key_value"],
            required=False,
            type=KeyValueType(),
            # help="If provided, sets only the specified configuration key non-interactively.",
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        remote_context_manager: RemoteContextManager,
        non_interactive_config_provider: NonInteractiveConfigProvider,
        interactive_config_provider: InteractiveConfigProvider,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._settings.enable_overwrite_mode()
        self._remote_context_manager = remote_context_manager
        self._non_interactive_config_provider = non_interactive_config_provider
        self._interactive_config_provider = interactive_config_provider

    def _save(self) -> None:
        self._remote_context_manager.commit()
        self._settings.save()
        self.stdout(
            f"Configuration file saved -> {self._settings.get_dir_path()}",
            severity=StdoutSeverity.SUCCESS,
        )

    def interactive_mode(self, from_env: Optional[str]) -> None:
        self._settings.replace_loader(
            loader=CompositeLoader(
                [
                    EnvFileLoader(from_env),
                    EnvVarLoader(),
                ]
            )
        )

        config_mappings = self._interactive_config_provider.get_all_configs()
        self._interactive_config_provider.apply_default_values(config_mappings)
        self._interactive_config_provider.recalculate_config_dynamic_values(config_mappings)
        self._save()

    def non_interactive_mode(self, config_key_value: tuple) -> None:
        key, value = config_key_value

        default_mappings = self._non_interactive_config_provider.get_all_configs()
        self._non_interactive_config_provider.raise_property_invalid(key)
        self._non_interactive_config_provider.apply_default_values(default_mappings)
        self._settings.set(key, value)
        self._non_interactive_config_provider.recalculate_config_dynamic_values(default_mappings)
        self._save()

    def run(
        self,
        from_env: Optional[str] = None,
        config_key_value: Optional[tuple] = None,
    ):
        if config_key_value:
            return self.non_interactive_mode(config_key_value)

        return self.interactive_mode(from_env=from_env)


class ConfigList(Command):
    name = "list"

    aliases = ["ls"]

    short_help = "Display all current configuration values used by the DAS CLI."

    help = """
NAME

    das-cli config list - Display current configuration settings

SYNOPSIS

    das-cli config list [key]

DESCRIPTION

    The 'das-cli config list' command prints all the current configuration settings
    that have been applied to the DAS CLI. The output is presented in a structured
    table format, which includes settings for various DAS components such as Redis,
    MongoDB, OpenFaaS, and others.

EXAMPLES

    To display the current configuration values, run:

        $ das-cli config list

    To display the value of a specific configuration key, run:

        $ das-cli config list services.query_agent.port

"""

    params = [
        CommandArgument(
            ["key"],
            required=False,
            type=str,
        ),
    ]

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def _show_config_key(self, key: str) -> None:
        value = self._settings.get(key, None)
        if value is None:
            self.stdout(
                f"The key '{key}' does not exist in the configuration file.",
                severity=StdoutSeverity.ERROR,
            )
        else:
            self.stdout(value)
            self.stdout(
                value,
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def _show_config(self) -> None:
        self.stdout(self._settings.pretty())
        self.stdout(
            self._settings.get_content(),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def run(self, key: Optional[str] = None):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        if not key:
            self._show_config()
        else:
            self._show_config_key(key)


class ConfigCli(CommandGroup):
    name = "config"

    aliases = ["cfg", "conf"]

    help = """
NAME

    das-cli config - Manage configuration settings

SYNOPSIS

    das-cli config [subcommand]

DESCRIPTION

    The 'das-cli config' command group provides a unified interface for managing
    the configuration settings of the DAS CLI. The configuration parameters include
    settings such as port numbers, usernames, container names, and clustering options
    for various services such as Redis, MongoDB, OpenFaaS, Jupyter Notebook, and more.

SUBCOMMANDS

    set
        Interactively set or update configuration parameters.
        See "das-cli config set" for more details.

    list
        Display the current configuration settings.
        See "das-cli config list" for more details.

USAGE

    To set the configuration values interactively:

        $ das-cli config set

    To list the current configuration settings:

        $ das-cli config list [key]
    """

    short_help = "Manage configuration settings for services used by the DAS CLI."

    @inject
    def __init__(
        self,
        configSet: ConfigSet,
        configList: ConfigList,
    ) -> None:
        super().__init__()

        self.add_commands(
            [
                configSet,
                configList,
            ]
        )
