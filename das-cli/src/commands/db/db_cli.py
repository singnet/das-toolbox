from typing import AnyStr, Union

from injector import inject

from common.factory.atomdb.atomdb_backend import AtomdbBackend, MongoDBRedisBackend, MorkMongoDBBackend

from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType

from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

from .db_service_response import DbServiceResponse


class DbCountAtoms(Command):
    name = "count-atoms"

    short_help = "Displays counts of MongoDB atoms and Redis key patterns."

    help = """
.SH NAME

count-atoms - Displays counts of MongoDB atoms and Redis key patterns.

.SH DESCRIPTION

'das-cli db count-atoms' counts the atoms stored in MongoDB and shows counts of specific key patterns stored in Redis.
This is useful for monitoring and understanding the distribution and number of records in your databases.

.SH EXAMPLES

Run the command see the count of MongoDB atoms and the breakdown of Redis key patterns:

$ das-cli db count-atoms

"""

    @inject
    def __init__(
        self,
        atomdb_backend: AtomdbBackend,
        mongodb_container_manager: MongodbContainerManager,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        self._atomdb_backend = atomdb_backend
        self._mongodb_container_manager = mongodb_container_manager
        self._redis_container_manager = redis_container_manager

        super().__init__()

    def _get_mongodb_container(self):
        return self._mongodb_container_manager.get_container()

    def _get_redis_container(self):
        return self._redis_container_manager.get_container()

    def _show_mongodb_stats(self):
        collection_stats = self._mongodb_container_manager.get_collection_stats()

        if len(collection_stats) < 1:
            self.stdout("MongoDB: No collections found (0)")
            return self.stdout(
                dict(
                    DbServiceResponse(
                        action="count-atoms",
                        status="no_collections_found",
                        message="No MongoDB collections found.",
                        container=self._get_mongodb_container(),
                        extra_details={
                            "stats": collection_stats,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        for key, count in collection_stats.items():
            self.stdout(f"MongoDB {key}: {count}")

        self.stdout(
            dict(
                DbServiceResponse(
                    action="count-atoms",
                    status="success",
                    message="Count of MongoDB atoms displayed successfully.",
                    container=self._get_mongodb_container(),
                    extra_details={
                        "stats": collection_stats,
                    },
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    @ensure_container_running(
        "_atomdb_backend",
        exception_text="\nPlease use 'db start' to start required services before running 'db count-atoms'.",
        verbose=False,
    )
    def run(self) -> None:
        for provider in self._atomdb_backend.get_active_providers():
            if isinstance(provider, MongoDBRedisBackend):
                self._show_mongodb_stats()

            elif isinstance(provider, MorkMongoDBBackend):
                self._show_mongodb_stats()


class DbStop(Command):
    name = "stop"

    params = [
        CommandOption(
            ["--prune", "-p"],
            is_flag=True,
            help="Remove volumes and force stop the containers.",
            default=False,
            required=False,
        ),
    ]

    short_help = "Stops all DBMS containers."

    help = """
.SH NAME

stop - Stops all DBMS containers.

.SH DESCRIPTION

'das-cli db stop' stops the DBMS containers that were previously started with 'das-cli db start'.
This command is useful for shutting down the databases when they are no longer needed.

IMPORTANT NOTE: After stopping the databases, all data will be lost.

.SH EXAMPLES

Stop DBMS containers previously started with 'das-cli db start'.

$ das-cli db stop

Stop DBMS containers and remove volumes.

$ das-cli db stop --prune

"""

    @inject
    def __init__(
        self,
        settings: Settings,
        atomdb_backend: AtomdbBackend,
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        morkdb_container_manager: MorkdbContainerManager,
    ) -> None:
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._morkdb_container_manager = morkdb_container_manager

        super().__init__()

    def _get_redis_container(self):
        return self._redis_container_manager.get_container()

    def _get_mongodb_container(self):
        return self._mongodb_container_manager.get_container()

    def _get_morkdb_container(self):
        return self._morkdb_container_manager.get_container()

    def _redis_node(
        self,
        context,
        ip,
        username,
        prune: bool = False,
    ):
        server_ip = self.get_execution_context().source.get("ip") or ip

        try:
            self._redis_container_manager.set_exec_context(context)
            self._redis_container_manager.stop(
                remove_volume=prune,
                force=prune,
            )
            self._redis_container_manager.unset_exec_context()

            self.stdout(
                f"The Redis service at {server_ip} has been stopped by the server user {username}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._get_redis_container().name
            self.stdout(
                f"The Redis service named {container_name} at {server_ip} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=f"The Redis service named {container_name} at {server_ip} is already stopped.",
                        container=self._get_redis_container(),
                        extra_details={
                            "node": {
                                "context": context,
                                "ip": ip,
                                "username": username,
                            },
                            "prune": prune,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def _redis(self, prune: bool = False) -> None:
        self.stdout("Stopping Redis service...")

        redis_nodes = self._settings.get("services.redis.nodes", [])
        redis_cluster = self._settings.get("services.redis.cluster", False)
        redis_container = self._get_redis_container()

        try:
            for redis_node in redis_nodes:
                self._redis_node(**redis_node, prune=prune)
        except DockerError as e:
            self.stdout(
                "\nError occurred while trying to stop Redis\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

        success_message = "Redis service stopped successfully"

        self.stdout(
            dict(
                DbServiceResponse(
                    action="stop",
                    status="success",
                    message=success_message,
                    extra_details={
                        "cluster": redis_cluster,
                        "nodes": redis_nodes,
                        "prune": prune,
                    },
                    container=redis_container,
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def _mongodb_node(
        self,
        context,
        ip,
        username,
        prune: bool = False,
    ) -> None:

        server_ip = self.get_execution_context().source.get("ip") or ip

        try:
            self._mongodb_container_manager.set_exec_context(context)
            self._mongodb_container_manager.stop(
                remove_volume=prune,
                force=prune,
            )
            self._mongodb_container_manager.unset_exec_context()

            self.stdout(
                f"The MongoDB service at {server_ip} has been stopped by the server user {username}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._get_mongodb_container().name
            warning_message = (
                f"The MongoDB service named {container_name} at {server_ip} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=self._get_mongodb_container(),
                        extra_details={
                            "node": {
                                "context": context,
                                "ip": ip,
                                "username": username,
                            }
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def _mongodb(self, prune: bool = False) -> None:
        self.stdout("Stopping MongoDB service...")

        mongodb_nodes = self._settings.get("services.mongodb.nodes", [])
        mongodb_cluster = self._settings.get("services.mongodb.cluster", False)

        try:
            for mongodb_node in mongodb_nodes:
                self._mongodb_node(**mongodb_node, prune=prune)

        except DockerError as e:
            self.stdout(
                "\nError occurred while trying to stop MongoDB\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

        success_message = "MongoDB service stopped successfully"

        self.stdout(
            dict(
                DbServiceResponse(
                    action="stop",
                    status="success",
                    message=success_message,
                    extra_details={
                        "cluster": mongodb_cluster,
                        "nodes": mongodb_nodes,
                        "prune": prune,
                    },
                    container=self._get_mongodb_container(),
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def _morkdb(self, prune: bool = False) -> None:
        self.stdout("Stopping MorkDB service...")

        try:
            self._morkdb_container_manager.stop(
                remove_volume=prune,
                force=prune,
            )

            success_message = "MorkDB service stopped successfully"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=self._get_morkdb_container(),
                        extra_details={
                            "prune": prune,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            container_name = self._get_morkdb_container().name
            warning_message = f"The MorkDB service named {container_name} is already stopped."
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=self._get_morkdb_container(),
                        extra_details={
                            "prune": prune,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError as e:
            self.stdout(
                "\nError occurred while trying to stop MorkDB\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def run(self, prune: bool = False) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        for provider in self._atomdb_backend.get_active_providers():
            if isinstance(provider, MongoDBRedisBackend):
                self._redis(prune)
                self._mongodb(prune)

            elif isinstance(provider, MorkMongoDBBackend):
                self._mongodb(prune)
                self._morkdb(prune)


class DbStart(Command):
    name = "start"

    short_help = "Starts all DBMS containers."

    help = """
.SH NAME

start - Starts all DBMS containers.

.SH DESCRIPTION

'das-cli db start' initiates all databases.

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
        atomdb_backend: AtomdbBackend,
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        morkdb_container_manager: MorkdbContainerManager,
    ) -> None:
        self._atomdb_backend = atomdb_backend
        self._settings = settings
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._morkdb_container_manager = morkdb_container_manager

        super().__init__()

    def _get_redis_container(self):
        return self._redis_container_manager.get_container()

    def _get_mongodb_container(self):
        return self._mongodb_container_manager.get_container()

    def _get_morkdb_container(self):
        return self._morkdb_container_manager.get_container()

    def _redis_node(
        self,
        redis_node: dict,
        redis_port: int,
        redis_cluster: bool,
    ) -> None:
        node_context = redis_node.get("context", "")
        node_ip = redis_node.get("ip", "")
        node_username = redis_node.get("username", "")
        public_ip = self.get_execution_context().source.get("ip") or node_ip

        try:

            if node_context and node_context != "default":
                self._redis_container_manager.set_exec_context(node_context)
            else:
                self._redis_container_manager.unset_exec_context()

            self._redis_container_manager.start_container(
                redis_port,
                node_username,
                node_ip,
                redis_cluster,
            )
            self._redis_container_manager.unset_exec_context()

            success_message = f"Redis has started successfully on port {redis_port} at {public_ip}, operating under the server user {node_username}."

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=self._redis_container_manager.get_container(),
                        extra_details={
                            "node": {
                                "context": node_context,
                                "ip": public_ip,
                                "username": node_username,
                            },
                            "cluster": redis_cluster,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        except DockerContainerDuplicateError:
            warning_message = f"Redis is already running. It is currently listening on port {redis_port} at {node_ip} under the server user {node_username}."
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=self._get_redis_container(),
                        extra_details={
                            "node": {
                                "context": node_context,
                                "ip": node_ip,
                                "username": node_username,
                            },
                            "cluster": redis_cluster,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        except DockerError:

            self.stdout(
                f"\nError occurred while trying to start Redis on port {redis_port} at {node_ip} under the server user {node_username}.\n",
                severity=StdoutSeverity.ERROR,
            )

    def _redis(self) -> None:
        self.stdout("Starting Redis service...")

        redis_port = self._settings.get("services.redis.port")
        redis_nodes = self._settings.get("services.redis.nodes", [])
        redis_cluster = self._settings.get("services.redis.cluster", False)

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

        self.stdout(
            dict(
                DbServiceResponse(
                    action="start",
                    status="success",
                    message=f"Redis started successfully on port {redis_port}",
                    extra_details={
                        "cluster": redis_cluster,
                        "nodes": redis_nodes,
                    },
                    container=self._get_redis_container(),
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def _mongodb_node(
        self,
        mongodb_node: dict,
        mongodb_port: int,
        mongodb_username: str,
        mongodb_password: str,
        is_cluster_enabled: bool = False,
        mongodb_cluster_secret_key: Union[AnyStr, None] = None,
    ) -> None:
        node_context = str(mongodb_node.get("context"))
        node_ip = str(mongodb_node.get("ip"))
        node_username = str(mongodb_node.get("username"))
        public_ip = self.get_execution_context().source.get("ip") or node_ip

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

            success_message = f"MongoDB has started successfully on port {mongodb_port} at {public_ip}, operating under the server user {node_username}."

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=self._get_mongodb_container(),
                        extra_details={
                            "node": {
                                "context": node_context,
                                "ip": public_ip,
                                "username": node_username,
                            },
                            "cluster": is_cluster_enabled,
                        },
                    ),
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = f"MongoDB is already running. It is currently listening on port {mongodb_port} at {public_ip} under the server user {node_username}."

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=self._get_mongodb_container(),
                        extra_details={
                            "node": {
                                "context": node_context,
                                "ip": node_ip,
                                "username": node_username,
                            },
                            "cluster": is_cluster_enabled,
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to start MongoDB on port {mongodb_port}\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def _mongodb(self) -> None:
        self.stdout("Starting MongoDB service...")

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        mongodb_nodes = self._settings.get("services.mongodb.nodes", [])
        mongodb_cluster = self._settings.get("services.mongodb.cluster", False)
        mongodb_cluster_secret_key = self._settings.get("services.mongodb.cluster_secret_key")

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

        self.stdout(
            dict(
                DbServiceResponse(
                    action="start",
                    status="success",
                    message=f"MongoDB started successfully on port {mongodb_port}",
                    container=self._mongodb_container_manager.get_container(),
                    extra_details={
                        "cluster": mongodb_cluster,
                        "nodes": mongodb_nodes,
                    },
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def _morkdb(self) -> None:
        self.stdout("Starting MorkDB service...")

        morkdb_port = self._settings.get("services.morkdb.port")

        try:
            self._morkdb_container_manager.start_container()

            success_message = f"MorkDB has started successfully on port {morkdb_port}"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=self._get_morkdb_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = (
                f"MorkDB is already running. It is currently listening on port {morkdb_port}"
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=self._get_mongodb_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError:
            self.stdout(
                f"\nError occurred while trying to start MorkDB on port {morkdb_port}.\n",
                severity=StdoutSeverity.ERROR,
            )

    def run(self):

        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        for provider in self._atomdb_backend.get_active_providers():

            if isinstance(provider, MongoDBRedisBackend):
                self._redis()
                self._mongodb()

            elif isinstance(provider, MorkMongoDBBackend):
                self._mongodb()
                self._morkdb()


class DbRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--prune", "-p"],
            is_flag=True,
            help="Remove volumes and force stop the containers.",
            default=False,
            required=False,
        ),
    ]

    short_help = "Restart all DBMS containers."

    help = """
.SH NAME

restart - Restart all DBMS containers.

.SH DESCRIPTION

'das-cli db restart' restarts all database containers previously started with 'das-cli db start'.
If no databases have been started, 'das-cli db restart' will simply start them.

IMPORTANT NOTE: Restarting the databases will result in all data being lost. Databases are started empty.

.SH EXAMPLES

Restart DBMS containers previously started with 'das-cli db start'.

$ das-cli db restart

Restart DBMS containers and remove their volumes.

$ das-cli db restart --prune

"""

    @inject
    def __init__(self, db_start: DbStart, db_stop: DbStop) -> None:
        super().__init__()
        self._db_start = db_start
        self._db_stop = db_stop

    def run(self, prune: bool = False):
        self._db_stop.run(prune)
        self._db_start.run()


class DbCli(CommandGroup):
    name = "database"

    aliases = ["db"]

    short_help = "Manage db-related operations."

    help = """
NAME

    das-cli db - Manage database-related operations for DAS.

SYNOPSIS

    das-cli db <command> [options]

DESCRIPTION

    Manage DAS backend DBMS required for for use with the DAS CLI.

    This command group allows you to control the lifecycle of local databases used by
    DAS components. It provides utilities to start, stop, and restart supported DBMSs.

COMMANDS

    start               Start the DAS database containers.
    stop                Stop the DAS database containers.
    restart             Restart the DAS database containers.
    count-atoms         Count the number of atoms currently stored in the database

EXAMPLES

    das-cli db start

        Start all DAS-related databases locally.

    das-cli db stop

        Stop all running DAS-related database containers.

    das-cli db restart

        Restart the DAS database services.

    das-cli db count-atoms

        Return the number of atoms currently stored in the database.
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
                db_start,
                db_stop,
                db_restart,
                db_count_atoms,
            ]
        )
