from typing import AnyStr, Union

from injector import inject

from common.decorators import ensure_container_running
from common import Command, CommandGroup, Settings, StdoutSeverity, CommandOption
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

from .mongodb_container_manager import MongodbContainerManager
from .redis_container_manager import RedisContainerManager


class DbCountAtoms(Command):
    name = "count-atoms"

    short_help = "Displays counts of MongoDB atoms and Redis key patterns."

    help = """
'das-cli db count-atoms' is a command that counts the atoms stored in MongoDB and shows counts of specific key patterns stored in Redis. This is useful for monitoring and understanding the distribution and number of records in your databases.

.SH OPTIONS

--verbose, -v
    Displays detailed information, including the count of atoms in MongoDB and the counts for various Redis key patterns.

.SH EXAMPLES

Run the command to get only the count of MongoDB atoms:

$ das-cli db count-atoms

Run the command with verbose output to see the count of MongoDB atoms and the breakdown of Redis key patterns:

$ das-cli db count-atoms --verbose

"""

    params = [
        CommandOption(
            ["--verbose", "-v"],
            is_flag=True,
            help="",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        mongodb_container_manager: MongodbContainerManager,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        self._mongodb_container_manager = mongodb_container_manager
        self._redis_container_manager = redis_container_manager

        super().__init__()

    def _show_verbose_output(self) -> None:
        collection_stats = self._mongodb_container_manager.get_collection_stats()
        redis_keys = self._redis_container_manager.get_count_keys().items()

        for key, count in collection_stats.items():
            self.stdout(f"MongoDB {key}: {count}")

        if len(redis_keys) < 1:
            return self.stdout("Redis: No keys found (0)")

        for redis_key, redis_count in redis_keys:
            self.stdout(f"Redis {redis_key}: {redis_count}")

    def _show_non_verbose_output(self) -> None:
        count_atoms = self._mongodb_container_manager.get_count_atoms()

        self.stdout(count_atoms)

    @ensure_container_running(
        [
            "_mongodb_container_manager",
            "_redis_container_manager",
        ],
        exception_text="\nPlease use 'db start' to start required services before running 'db count-atoms'.",
        verbose=False,
    )
    def run(self, verbose: bool) -> None:
        if verbose:
            return self._show_verbose_output()

        return self._show_non_verbose_output()


class DbStop(Command):
    name = "stop"

    short_help = "Stops all DBMS containers."

    help = """
'das-cli db stop' stops the DBMS containers that were previously started with the 'das-cli db start'.
This command is useful for shutting down the databases when they are no longer needed.

IMPORTANT NOTE: After stopping the databases, all data will be lost.

.SH EXAMPLES

Stop DBMS containers previously started with 'das-cli db start'.

$ das-cli db stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager

    def _redis_node(self, context, ip, username):
        try:
            self._redis_container_manager.set_exec_context(context)
            self._redis_container_manager.stop()
            self._redis_container_manager.unset_exec_context()

            self.stdout(
                f"The Redis service at {ip} has been stopped by the server user {username}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._redis_container_manager.get_container().name
            self.stdout(
                f"The Redis service named {container_name} at {ip} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def _redis(self):
        self.stdout("Stopping Redis service...")

        redis_nodes = self._settings.get("redis.nodes", [])

        try:
            for redis_node in redis_nodes:
                self._redis_node(**redis_node)
        except DockerError as e:
            self.stdout(
                "\nError occurred while trying to stop Redis\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def _mongodb_node(self, context, ip, username):
        try:
            self._mongodb_container_manager.set_exec_context(context)
            self._mongodb_container_manager.stop()
            self._mongodb_container_manager.unset_exec_context()

            self.stdout(
                f"The MongoDB service at {ip} has been stopped by the server user {username}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._mongodb_container_manager.get_container().name
            self.stdout(
                f"The MongoDB service named {container_name} at {ip} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def _mongodb(self):
        self.stdout("Stopping MongoDB service...")

        mongodb_nodes = self._settings.get("mongodb.nodes", [])

        try:
            for mongodb_node in mongodb_nodes:
                self._mongodb_node(**mongodb_node)

        except DockerError as e:
            self.stdout(
                "\nError occurred while trying to stop MongoDB\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def run(self):
        self._settings.raise_on_missing_file()

        self._redis()
        self._mongodb()


class DbStart(Command):
    name = "start"

    short_help = "Starts all DBMS containers."

    help = """
'das-cli db start' initiates all databases.
These databases can either be utilized alongside DAS FaaS Function or connected directly to a local DAS instance.

Upon execution, the command will display the ports on which each database is running.
Note that the port configuration can be modified using the 'das-cli config set' command.

.SH EXAMPLES

Start all databases for use with the DAS.

$ das-cli db start
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager

    def _redis_node(
        self,
        redis_node: dict,
        redis_port: int,
        redis_cluster: bool,
    ) -> None:
        node_context = redis_node.get("context")
        node_ip = redis_node.get("ip")
        node_username = redis_node.get("username")

        try:
            self._redis_container_manager.set_exec_context(node_context)
            self._redis_container_manager.start_container(redis_port, redis_cluster)
            self._redis_container_manager.unset_exec_context()

            self.stdout(
                f"Redis has started successfully on port {redis_port} at {node_ip}, operating under the server user {node_username}.",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Redis is already running. It is currently listening on port {redis_port} at {node_ip} under the server user {node_username}.",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError:
            self.stdout(
                f"\nError occurred while trying to start Redis on port {redis_port} at {node_ip} under the server user {node_username}.\n",
                severity=StdoutSeverity.ERROR,
            )

    def _redis(self) -> None:
        self.stdout("Starting Redis service...")

        redis_port = self._settings.get("redis.port")
        redis_nodes = self._settings.get("redis.nodes", [])
        redis_cluster = self._settings.get("redis.cluster", False)

        for redis_node in redis_nodes:
            self._redis_node(redis_node, redis_port, redis_cluster)

        if redis_cluster:
            try:
                self._redis_container_manager.start_cluster(redis_nodes, redis_port)
            except Exception as e:
                self.stdout(
                    "\nFailed to start the cluster. Please check the conectivity between the nodes and try again.\n",
                    severity=StdoutSeverity.ERROR,
                )
                raise e

    def _mongodb_node(
        self,
        mongodb_node: dict,
        mongodb_port: int,
        mongodb_username: str,
        mongodb_password: str,
        is_cluster_enabled: bool = False,
        mongodb_cluster_secret_key: Union[AnyStr, None] = None,
    ) -> None:
        node_context = mongodb_node.get("context")
        node_ip = mongodb_node.get("ip")
        node_username = mongodb_node.get("username")

        cluster_node = (
            dict(
                host=node_ip,
                username=node_username,
            )
            if is_cluster_enabled
            else None
        )

        try:
            self._mongodb_container_manager.set_exec_context(node_context)
            self._mongodb_container_manager.start_container(
                mongodb_port,
                mongodb_username,
                mongodb_password,
                cluster_node,
                mongodb_cluster_secret_key,
            )
            self._mongodb_container_manager.unset_exec_context()

            self.stdout(
                f"MongoDB has started successfully on port {mongodb_port} at {node_ip}, operating under the server user {node_username}.",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"MongoDB is already running. It is currently listening on port {mongodb_port} at {node_ip} under the server user {node_username}.",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to start MongoDB on port {mongodb_port}\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def _mongodb(self) -> None:
        self.stdout("Starting MongoDB service...")

        mongodb_port = self._settings.get("mongodb.port")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")
        mongodb_nodes = self._settings.get("mongodb.nodes", [])
        mongodb_cluster = self._settings.get("mongodb.cluster", False)
        mongodb_cluster_secret_key = self._settings.get("mongodb.cluster_secret_key")

        for mongodb_node in mongodb_nodes:
            self._mongodb_node(
                mongodb_node,
                mongodb_port,
                mongodb_username,
                mongodb_password,
                mongodb_cluster,
                mongodb_cluster_secret_key,
            )

        if mongodb_cluster:
            try:
                self._mongodb_container_manager.start_cluster(
                    mongodb_nodes,
                    mongodb_port,
                    mongodb_username,
                    mongodb_password,
                )
            except Exception as e:
                self.stdout(
                    "\nFailed to start the cluster. Please check the conectivity between the nodes and try again.\n",
                    severity=StdoutSeverity.ERROR,
                )
                raise e

    def run(self):
        self._settings.raise_on_missing_file()

        self._redis()
        self._mongodb()


class DbRestart(Command):
    name = "restart"

    short_help = "Restart all DBMS containers."

    help = """
'das-cli db restart' restarts all database containers previously started with
'das-cli start'. If no database have been started, 'das-cli db restart' just
start them.

IMPORTANTE NOTE: Restarting the databases will result in all data being lost. Databases are started empty.

.SH EXAMPLES

Restart DBMS containers previously started with the 'das-cli db start'.

$ das-cli db restart
"""

    @inject
    def __init__(self, db_start: DbStart, db_stop: DbStop) -> None:
        super().__init__()
        self._db_start = db_start
        self._db_stop = db_stop

    def run(self):
        self._db_stop.run()
        self._db_start.run()


class DbCli(CommandGroup):
    name = "db"

    short_help = "Manage db-related operations."

    help = """
        'das-cli db' commands allow you to manage DAS backend DBMSs for use
        with the DAS CLI. 'das-cli db' provides commands to start, stop, and
        restart the databases as needed.
        """

    @inject
    def __init__(
        self,
        db_start: DbStart,
        db_stop: DbStop,
        db_restart: DbRestart,
        db_count_atoms: DbCountAtoms,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                db_start.command,
                db_stop.command,
                db_restart.command,
                db_count_atoms.command,
            ]
        )
