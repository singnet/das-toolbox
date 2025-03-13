from typing import Dict, List

from injector import inject

from common import (
    Command,
    CommandGroup,
    IntRange,
    ReachableIpAddress,
    RemoteContextManager,
    Settings,
    StdoutSeverity,
    get_public_ip,
    get_rand_token,
    get_server_username,
)
from common.docker.remote_context_manager import Server


class ConfigSet(Command):
    name = "set"

    short_help = "'das-cli config set' Sets configuration parameters for DAS CLI."

    help = """
'das-cli config set' prompts the user for configuration settings for the DAS CLI.
These settings include parameters such as port numbers, usernames, and other relevant information required by various DAS components.
The command displays prompts for each configuration option, suggesting default values when available.
If the user has already configured a setting, the default value will be the previously set value, allowing for quick modifications.
Once all configurations are provided, the command will also inform the user about the location where the configuration file was created.
This file contains several variables that influence the behavior of DAS commands based on the user's provided parameters.

.SH EXAMPLES

Set configuration settings for the DAS CLI.

$ das-cli config set

.SH VARIABLES

redis.*
    These variables control Redis settings, such as:

    redis.port
        Defines the port number on which the Redis server is listening. The user must ensure this port is available on the server where das-cli is running and also on other nodes if a cluster is being used. If using a firewall like `ufw`, the user can allow the necessary ports for cluster communication using the command `ufw allow 7000:17000/tcp` to ensure proper communication within the cluster, assuming the Redis instance operates on port 7000. It's recommended to restrict access to specific IP addresses for each node. This practice enhances security and minimizes potential vulnerabilities.

    redis.container_name
        Specifies the name of the Docker container running the Redis server.

    redis.cluster
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

    mongodb.cluster
        Indicates whether a MongoDB cluster is being used (true/false).

    mongodb.cluster_secret_key
        This key is uploaded to all nodes within the MongoDB cluster. It is used for mutual authentication between nodes, ensuring that only authorized nodes can communicate with each other.

    mongodb.nodes
        Receives a list of nodes for MongoDB configuration. For a single-node setup, there must be at least one node specified with the default context. For a cluster setup, there must be at least three nodes specified. Additionally, it is necessary to configure an SSH key and utilize this key on each node to ensure SSH connectivity between them. This is essential because Docker communicates between nodes remotely to deploy images with MongoDB. To establish SSH connectivity, generate an SSH key using `ssh-keygen` and add this key to all servers in the cluster. Ensure that port 22 is open on all servers to allow SSH connections.

    mongodb.nodes.[].context
        The name of the Docker context containing connection information for the remote Docker instances of other nodes.

    mongodb.nodes.[].ip
        The IP address of the node.

    mongodb.nodes.[].username
        The username for connecting to the node.

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

das_peer.*
    These variables configure settings for the DAS Peer, such as:

    das_peer.container_name
        Specifies the Docker container name for the DAS peer, which acts as the main server. This name is essential for managing and communicating with the DAS peer container.

dbms_peer.*
    These variables configure settings for the DBMS Peer, such as:

    dbms_peer.container_name
        Specifies the Docker container name for the DBMS peer, which connects to the DAS peer to send data.
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        remote_context_manager: RemoteContextManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._remote_context_manager = remote_context_manager

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
                use_default_as_context=False,
            )

        nodes = self._build_cluster(port)

        return nodes

    def _build_cluster(
        self,
        port: int,
        min_nodes: int = 3,
    ) -> List[Dict]:
        current_nodes = self._settings.get("redis.nodes", [])
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

            server_ip_default = current_nodes[i]["ip"] if i < len(current_nodes) else None
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
            servers=self._settings.get("redis.nodes", []),
        )

        return redis_nodes

    def _redis(self) -> Dict:
        redis_port = self.prompt(
            "Enter Redis port",
            default=self._settings.get("redis.port", 6379),
            type=int,
        )
        cluster_default_value = self._settings.get("redis.cluster", False)
        redis_cluster = self.confirm(
            "Is it a Redis cluster?",
            default=cluster_default_value,
        )
        return {
            "redis.port": redis_port,
            "redis.container_name": f"das-cli-redis-{redis_port}",
            "redis.cluster": redis_cluster,
            "redis.nodes": lambda: self._redis_nodes(redis_cluster, redis_port),
        }

    def _mongodb_nodes(self, mongodb_cluster, mongodb_port) -> List[Dict]:
        mongodb_nodes = self._build_nodes(mongodb_cluster, mongodb_port)

        self._destroy_contexts(
            servers=self._settings.get("mongodb.nodes", []),
        )

        return mongodb_nodes

    def _mongodb(self) -> dict:
        mongodb_port = self.prompt(
            "Enter MongoDB port",
            default=self._settings.get("mongodb.port", 27017),
            type=int,
        )
        mongodb_username = self.prompt(
            "Enter MongoDB username",
            default=self._settings.get("mongodb.username", "admin"),
        )
        mongodb_password = self.prompt(
            "Enter MongoDB password",
            # hide_input=True, # When hide_input is set I cannot set the answers based on a text file making impossible to test this command
            default=self._settings.get("mongodb.password", "admin"),
        )
        cluster_default_value = self._settings.get("mongodb.cluster", False)
        is_mongodb_cluster = self.confirm(
            "Is it a MongoDB cluster?",
            default=cluster_default_value,
        )
        cluster_secret_key = self._settings.get(
            "mongodb.cluster_secret_key",
            get_rand_token(num_bytes=15),
        )
        return {
            "mongodb.port": mongodb_port,
            "mongodb.container_name": f"das-cli-mongodb-{mongodb_port}",
            "mongodb.username": mongodb_username,
            "mongodb.password": mongodb_password,
            "mongodb.cluster": is_mongodb_cluster,
            "mongodb.nodes": lambda: self._mongodb_nodes(
                is_mongodb_cluster,
                mongodb_port,
            ),
            "mongodb.cluster_secret_key": cluster_secret_key,
        }

    def _loader(self) -> dict:
        return {"loader.container_name": "das-cli-loader"}

    def _das_peer(self) -> dict:
        database_adapter_server_port = 30100

        return {
            "das_peer.container_name": f"das-cli-das-peer-{database_adapter_server_port}",
            "das_peer.port": database_adapter_server_port,
        }

    def _dbms_peer(self) -> dict:
        return {
            "dbms_peer.container_name": "das-cli-dbms-peer",
        }

    def _openfaas(self) -> dict:
        return {
            "openfaas.container_name": "das-cli-openfaas-8080",
            "openfaas.version": "latest",
            "openfaas.function": "query-engine",  # TODO: CHANGE TO ENUM
        }

    def _jupyter_notebook(self) -> dict:
        jupyter_notebook_port = self.prompt(
            "Enter Jupyter Notebook port",
            default=self._settings.get("jupyter.port", 8888),
        )

        return {
            "jupyter_notebook.port": jupyter_notebook_port,
            "jupyter_notebook.container_name": f"das-cli-jupyter-notebook-{jupyter_notebook_port}",
        }

    def _attention_broker(self) -> dict:
        attention_broker_port = self.prompt(
            "Enter the Attention Broker port",
            default=self._settings.get("attention_broker.port", 37007),
        )

        return {
            "attention_broker.port": attention_broker_port,
            "attention_broker.container_name": f"das-cli-attention-broker-{attention_broker_port}",
        }

    def _query_agent(self) -> dict:
        query_agent_port = self.prompt(
            "Enter the Query Agent port",
            default=self._settings.get("query_agent.port", 35700),
        )

        return {
            "query_agent.port": query_agent_port,
            "query_agent.container_name": f"das-cli-query-agent-{query_agent_port}",
        }

    def _link_creation_agent(self) -> dict:
        return {
            "link_creation_agent.container_name": f"das-cli-link-creation-agent",
        }

    def _save(self) -> None:
        self._remote_context_manager.commit()
        self._settings.save()
        self.stdout(
            f"Configuration file saved -> {self._settings.get_dir_path()}",
            severity=StdoutSeverity.SUCCESS,
        )

    def run(self):
        config_steps = [
            self._redis,
            self._mongodb,
            self._loader,
            self._das_peer,
            self._dbms_peer,
            self._openfaas,
            self._jupyter_notebook,
            self._attention_broker,
            self._query_agent,
            self._link_creation_agent,
        ]

        for config_step in config_steps:
            config = config_step()
            self._set_config(config)

        self._save()


class ConfigList(Command):
    name = "list"

    short_help = "'das-cli config list' displays current configuration settings."

    help = """
'das-cli config list' displays current configuration settings.

.SH EXAMPLES

Display current configuration settings

$ das-cli config list
"""

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def run(self):
        self._settings.raise_on_missing_file()

        settings_table = self._settings.pretty()

        self.stdout(settings_table)


class ConfigCli(CommandGroup):
    name = "config"

    help = """
'das-cli config' allows you to manage configuration settings for the DAS CLI, with commands to set, list, and modify
parameters such as port numbers, usernames and other configuration settings required by various DAS components.
    """

    short_help = "'das-cli config' allows you to manage configuration settings for the DAS CLI"

    @inject
    def __init__(
        self,
        configSet: ConfigSet,
        configList: ConfigList,
    ) -> None:
        super().__init__()

        self.add_commands(
            [
                configSet.command,
                configList.command,
            ]
        )
