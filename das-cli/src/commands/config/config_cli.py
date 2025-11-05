from typing import Dict, List, Optional

from injector import inject

from common import (
    Command,
    CommandArgument,
    CommandGroup,
    CommandOption,
    IntRange,
    ReachableIpAddress,
    RemoteContextManager,
    KeyValueType,
    Settings,
    StdoutSeverity,
    StdoutType,
    get_public_ip,
    get_rand_token,
    get_server_username,
)
from common.config.loader import CompositeLoader, EnvFileLoader, EnvVarLoader
from common.docker.remote_context_manager import Server
from common.prompt_types import AbsolutePath

# from common.utils import get_schema_hash
from .default_config_provider import DefaultConfigProvider


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
        default_config_provider: DefaultConfigProvider,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._settings.enable_overwrite_mode()
        self._remote_context_manager = remote_context_manager
        self._default_config_provider = default_config_provider

    def _set_config(self, config_dict):
        for key, value in config_dict.items():
            if callable(value):
                self._settings.set(key, value())
            else:
                self._settings.set(key, value)

    def _build_localhost_node(
        self,
        ip: str = "localhost",
        use_default_as_context: bool = True,
    ) -> List[Dict]:
        server_user = get_server_username()

        node = Server(
            {
                "ip": ip,
                "username": server_user,
            }
        )

        if not use_default_as_context:
            return self._remote_context_manager.create_servers_context([node])

        return [
            {
                "context": "default",
                **node,
            }
        ]

    def _build_nodes(self, is_cluster: bool, port: int) -> List[Dict]:
        if not is_cluster:
            return self._build_localhost_node()

        nodes = []

        join_current_server = self.confirm(
            "Do you want to join the current server as an actual node on the network?",
            default=True,
        )

        if join_current_server:
            server_public_ip = get_public_ip()

            if server_public_ip is None:
                raise Exception(
                    "The server's public ip could not be solved. Make sure it has internet access."
                )

            nodes += self._build_localhost_node(
                server_public_ip,
                use_default_as_context=True,
            )

        nodes += self._build_cluster(port, min_nodes=3 - len(nodes))

        return nodes

    def _build_cluster(
        self,
        port: int,
        min_nodes: int = 3,
    ) -> List[Dict]:
        current_nodes = self._settings.get("services.redis.nodes", [])
        current_total_nodes = len(current_nodes)
        total_nodes_default = current_total_nodes if current_total_nodes > 3 else 3

        total_nodes = self.prompt(
            f"Enter the total number of nodes for the cluster (>= {min_nodes})",
            hide_input=False,
            type=IntRange(min_nodes),
            default=total_nodes_default,
        )

        servers: List[Server] = []
        for i in range(0, total_nodes):
            server_username_default = (
                current_nodes[i]["username"] if i < len(current_nodes) else None
            )
            server_username = self.prompt(
                f"Enter the server username for the server-{i + 1}",
                hide_input=False,
                default=server_username_default,
            )

            server_ip_default = (
                current_nodes[i]["ip"] if i < len(current_nodes) else None
            )
            server_ip = self.prompt(
                f"Enter the ip address for the server-{i + 1}",
                hide_input=False,
                type=ReachableIpAddress(server_username, port),
                default=server_ip_default,
            )

            servers.append(
                {
                    "ip": server_ip,
                    "username": server_username,
                }
            )

        return self._remote_context_manager.create_servers_context(servers)

    def _destroy_contexts(self, servers: List[Dict]):
        server_contexts = [server.get("context", "") for server in servers]
        self._remote_context_manager.remove_servers_context(server_contexts)

    def _redis_nodes(self, redis_cluster, redis_port) -> List[Dict]:
        redis_nodes = self._build_nodes(redis_cluster, redis_port)

        self._destroy_contexts(
            servers=self._settings.get("services.redis.nodes", []),
        )

        return redis_nodes

    def _redis(self) -> Dict:
        redis_port = self.prompt(
            "Enter Redis port",
            default=self._settings.get("services.redis.port", 40020),
            type=int,
        )
        cluster_default_value = self._settings.get("services.redis.cluster", False)
        redis_cluster = self.confirm(
            "Is it a Redis cluster?",
            default=cluster_default_value,
        )
        return {
            "services.redis.port": redis_port,
            "services.redis.container_name": f"das-cli-redis-{redis_port}",
            "services.redis.cluster": redis_cluster,
            "services.redis.nodes": lambda: self._redis_nodes(
                redis_cluster, redis_port
            ),
        }

    def _mongodb_nodes(self, mongodb_cluster, mongodb_port) -> List[Dict]:
        mongodb_nodes = self._build_nodes(mongodb_cluster, mongodb_port)

        self._destroy_contexts(
            servers=self._settings.get("services.mongodb.nodes", []),
        )

        return mongodb_nodes

    def _mongodb(self) -> dict:
        mongodb_port = self.prompt(
            "Enter MongoDB port",
            default=self._settings.get("services.mongodb.port", 40021),
            type=int,
        )
        mongodb_username = self.prompt(
            "Enter MongoDB username",
            default=self._settings.get("services.mongodb.username", "admin"),
        )
        mongodb_password = self.prompt(
            "Enter MongoDB password",
            # hide_input=True, # When hide_input is set I cannot set the answers based on a text file making impossible to test this command
            default=self._settings.get("services.mongodb.password", "admin"),
        )
        cluster_default_value = self._settings.get("services.mongodb.cluster", False)
        is_mongodb_cluster = self.confirm(
            "Is it a MongoDB cluster?",
            default=cluster_default_value,
        )
        cluster_secret_key = self._settings.get(
            "services.mongodb.cluster_secret_key",
            get_rand_token(num_bytes=15),
        )
        return {
            "services.mongodb.port": mongodb_port,
            "services.mongodb.container_name": f"das-cli-mongodb-{mongodb_port}",
            "services.mongodb.username": mongodb_username,
            "services.mongodb.password": mongodb_password,
            "services.mongodb.cluster": is_mongodb_cluster,
            "services.mongodb.nodes": lambda: self._mongodb_nodes(
                is_mongodb_cluster,
                mongodb_port,
            ),
            "services.mongodb.cluster_secret_key": cluster_secret_key,
        }

    def _loader(self) -> dict:
        return {"services.loader.container_name": "das-cli-loader"}

    def _das_peer(self) -> dict:
        database_adapter_server_port = 40018

        return {
            "services.das_peer.container_name": f"das-cli-das-peer-{database_adapter_server_port}",
            "services.das_peer.port": database_adapter_server_port,
        }

    def _dbms_peer(self) -> dict:
        return {
            "services.dbms_peer.container_name": "das-cli-dbms-peer",
        }

    def _jupyter_notebook(self) -> dict:
        jupyter_notebook_port = self.prompt(
            "Enter Jupyter Notebook port",
            default=self._settings.get("services.jupyter.port", 40019),
        )

        return {
            "services.jupyter_notebook.port": jupyter_notebook_port,
            "services.jupyter_notebook.container_name": f"das-cli-jupyter-notebook-{jupyter_notebook_port}",
        }

    def _attention_broker(self) -> dict:
        attention_broker_port = self.prompt(
            "Enter the Attention Broker port",
            default=self._settings.get("services.attention_broker.port", 40001),
        )

        return {
            "services.attention_broker.port": attention_broker_port,
            "services.attention_broker.container_name": f"das-cli-attention-broker-{attention_broker_port}",
        }

    def _query_agent(self) -> dict:
        query_agent_port = self.prompt(
            "Enter the Query Agent port",
            default=self._settings.get("services.query_agent.port", 40002),
        )

        return {
            "services.query_agent.port": query_agent_port,
            "services.query_agent.container_name": f"das-cli-query-agent-{query_agent_port}",
        }

    def _link_creation_agent(self) -> dict:
        link_creation_agent_port = self.prompt(
            "Enter the Link Creation Agent Server port",
            default=self._settings.get("services.link_creation_agent.port", 40003),
        )

        return {
            "services.link_creation_agent.container_name": f"das-cli-link-creation-agent-{link_creation_agent_port}",
            "services.link_creation_agent.port": link_creation_agent_port,
        }

    def _inference_agent(self) -> dict:
        inference_agent_port = self.prompt(
            "Enter the Inference Agent port",
            default=self._settings.get("services.inference_agent.port", 40004),
        )

        return {
            "services.inference_agent.port": inference_agent_port,
            "services.inference_agent.container_name": f"das-cli-inference-agent-{inference_agent_port}",
        }

    def _evolution_agent(self) -> dict:
        evolution_agent_port = self.prompt(
            "Enter the Evolution agent port",
            default=self._settings.get("services.evolution_agent.port", 40005),
        )

        return {
            "services.evolution_agent.port": evolution_agent_port,
            "services.evolution_agent.container_name": f"das-cli-evolution-agent-{evolution_agent_port}",
        }

    def _context_broker(self) -> dict:
        context_broker_port = self.prompt(
            "Enter the Context Broker port",
            default=self._settings.get("services.context_broker.port", 40006),
        )

        return {
            "services.context_broker.port": context_broker_port,
            "services.context_broker.container_name": f"das-cli-context-broker-{context_broker_port}",
        }

    def _schema_hash(self) -> dict:
        # schema_hash = get_schema_hash()
        return {"schema_hash": None}

    def _save(self) -> None:
        self._remote_context_manager.commit()
        self._settings.save()
        self.stdout(
            f"Configuration file saved -> {self._settings.get_dir_path()}",
            severity=StdoutSeverity.SUCCESS,
        )

    def _morkdb(self) -> Dict:
        morkdb_port = self.prompt(
            "Enter the MorkDB port",
            default=self._settings.get("services.morkdb.port", 40022),
        )

        return {
            "services.morkdb.port": morkdb_port,
            "services.morkdb.container_name": f"das-cli-morkdb-{morkdb_port}",
        }

    def _atomdb_backend(self) -> dict:
        backends = {
            "redis_mongodb": {
                self._redis,
                self._mongodb,
            },
            "mork_mongodb": {
                self._mongodb,
                self._morkdb,
            },
        }

        atomdb_backend = self.select(
            text="Choose the AtomDB backend: ",
            options={
                "MongoDB + Redis": "redis_mongodb",
                "MongoDB + Mork": "mork_mongodb",
            },
            default=self._settings.get(
                "services.database.atomdb_backend", "redis_mongodb"
            ),
        )

        backend = backends.get(atomdb_backend) or backends["redis_mongodb"]
        backend_configs = [func() for func in backend]
        merged_config = {
            "services.database.atomdb_backend": atomdb_backend,
        }
        for config in backend_configs:
            merged_config.update(config)

        return merged_config

    def interactive_mode(self, from_env: str) -> None:
        self._settings.replace_loader(
            loader=CompositeLoader(
                [
                    EnvFileLoader(from_env),
                    EnvVarLoader(),
                ]
            )
        )

        config_steps = [
            self._schema_hash,
            self._atomdb_backend,
            self._loader,
            self._das_peer,
            self._dbms_peer,
            self._jupyter_notebook,
            self._attention_broker,
            self._query_agent,
            self._link_creation_agent,
            self._inference_agent,
            self._evolution_agent,
            self._context_broker,
        ]

        for config_step in config_steps:
            config = config_step()
            self._set_config(config)

        self._save()

    def _apply_default_values(self, default_mappings: Dict):
        for default_key, default_value_or_func in default_mappings.items():
            if self._settings._store.get(default_key) is not None:
                continue

            if callable(default_value_or_func):
                if "nodes" in default_key:
                    calculated_value = default_value_or_func(self._settings)
                    self._settings.set(default_key, calculated_value)
                continue
            else:
                self._settings.set(default_key, default_value_or_func)

    def _recalculate_config_dynamic_values(self, default_mappings: Dict):
        for default_key, default_value_or_func in default_mappings.items():
            if callable(default_value_or_func):

                if "nodes" in default_key:
                    continue

                calculated_value = default_value_or_func(self._settings)

                self._settings.set(default_key, calculated_value)

    def _raise_property_invalid(self, key: str, default_mappings: Dict):
        properties = default_mappings.keys()
        if key not in properties:
            raise AttributeError()

    def non_interactive_mode(self, config_key_value: tuple) -> None:
        key, value = config_key_value

        try:
            default_mappings = self._default_config_provider.get_all_default_mappings()

            self._raise_property_invalid(key, default_mappings)

            self._apply_default_values(default_mappings)

            self._settings.set(key, value)
            self._recalculate_config_dynamic_values(default_mappings)

            self._save()
        except AttributeError:
            raise AttributeError(f"'{key}' is not a valid configuration property.")

    def run(
        self,
        from_env: Optional[str] = None,
        config_key_value: Optional[str] = None,
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
