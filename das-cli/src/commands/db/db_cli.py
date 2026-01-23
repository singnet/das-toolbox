from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)

from .db_docs import (
    HELP_DB_CLI,
    HELP_DB_COUNT_ATOMS,
    HELP_DB_RESTART,
    HELP_DB_START,
    HELP_DB_STOP,
    SHORT_HELP_DB_CLI,
    SHORT_HELP_DB_COUNT_ATOMS,
    SHORT_HELP_DB_RESTART,
    SHORT_HELP_DB_START,
    SHORT_HELP_DB_STOP,
)
from .db_service_response import DbServiceResponse


class DbCountAtoms(Command):
    name = "count-atoms"

    short_help = SHORT_HELP_DB_COUNT_ATOMS

    help = HELP_DB_COUNT_ATOMS

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

    short_help = SHORT_HELP_DB_STOP
    help = HELP_DB_STOP

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

    def _get_container(self, service: str):
        return {
            "redis": self._redis_container_manager.get_container,
            "mongodb": self._mongodb_container_manager.get_container,
            "morkdb": self._morkdb_container_manager.get_container,
        }[service.lower()]()

    def _stop_node(
        self, manager, context: str, ip: str, username: str, prune: bool, service_name: str
    ):

        server_ip = self.get_execution_context().source.get("ip") or ip

        try:
            manager.set_exec_context(context)
            manager.stop(remove_volume=prune, force=prune)
            manager.unset_exec_context()
            self.stdout(
                f"The {service_name} service at {server_ip} has been stopped by the server user {username}",
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            container_name = manager.get_container().name
            warning_msg = f"The {service_name} service named {container_name} at {server_ip} is already stopped."
            self.stdout(warning_msg, severity=StdoutSeverity.WARNING)
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_msg,
                        container=manager.get_container(),
                        extra_details={
                            "node": {"context": context, "ip": ip, "username": username},
                        },
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def _stop_service(
        self, manager, nodes: list, service_name: str, prune: bool = False, cluster: bool = False
    ):

        self.stdout(f"Stopping {service_name} service...")

        try:
            for node in nodes:
                self._stop_node(manager, **node, prune=prune, service_name=service_name)
        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to stop {service_name}\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

        success_msg = f"{service_name} service stopped successfully"
        self.stdout(
            dict(
                DbServiceResponse(
                    action="stop",
                    status="success",
                    message=success_msg,
                    container=self._get_container(service_name),
                    extra_details={"cluster": cluster, "nodes": nodes, "prune": prune},
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def run(self, prune: bool = False) -> None:
        self._settings.validate_configuration_file()

        for provider in self._atomdb_backend.get_active_providers():

            if isinstance(provider, MongoDBRedisBackend):
                self._stop_service(
                    self._redis_container_manager,
                    self._settings.get("services.redis.nodes", []),
                    "Redis",
                    prune,
                    self._settings.get("services.redis.cluster", False),
                )
                self._stop_service(
                    self._mongodb_container_manager,
                    self._settings.get("services.mongodb.nodes", []),
                    "MongoDB",
                    prune,
                    self._settings.get("services.mongodb.cluster", False),
                )

            elif isinstance(provider, MorkMongoDBBackend):
                self._stop_service(
                    self._mongodb_container_manager,
                    self._settings.get("services.mongodb.nodes", []),
                    "MongoDB",
                    prune,
                    self._settings.get("services.mongodb.cluster", False),
                )
                self._stop_service(self._morkdb_container_manager, [{}], "MorkDB", prune)


class DbStart(Command):
    name = "start"
    short_help = SHORT_HELP_DB_START
    help = HELP_DB_START

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

    def _get_container(self, service: str):

        return {
            "redis": self._redis_container_manager.get_container,
            "mongodb": self._mongodb_container_manager.get_container,
            "morkdb": self._morkdb_container_manager.get_container,
        }[service.lower()]()

    def _start_node(self, container_manager, node: dict, service_name: str, **kwargs):

        node_context = node.get("context", "")
        node_ip = node.get("ip", "")
        node_username = node.get("username", "")
        public_ip = self.get_execution_context().source.get("ip") or node_ip
        container_port = kwargs["port"]

        try:
            if node_context and node_context != "default":
                container_manager.set_exec_context(node_context)
            else:
                container_manager.unset_exec_context()

            if service_name.lower() == "redis":
                container_manager.start_container(
                    container_port, node_username, node_ip, kwargs.get("cluster", False)
                )
            elif service_name.lower() == "mongodb":
                container_manager.start_container(
                    container_port,
                    kwargs["username"],
                    kwargs["password"],
                    kwargs.get("cluster_node"),
                    kwargs.get("cluster_key"),
                )

            elif service_name == "morkdb":
                container_manager.start_container()

            container_manager.unset_exec_context()

            success_msg = f"{service_name} has started successfully on port {container_port} at {public_ip}, operating under the server user {node_username}."
            self.stdout(success_msg, severity=StdoutSeverity.SUCCESS)
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="success",
                        message=success_msg,
                        container=container_manager.get_container(),
                        extra_details=node,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        except DockerContainerDuplicateError:
            warning_msg = f"{service_name} is already running. It is currently listening on port {container_port} at {public_ip} under the server user {node_username}."
            self.stdout(warning_msg, severity=StdoutSeverity.WARNING)
            self.stdout(
                dict(
                    DbServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_msg,
                        container=container_manager.get_container(),
                        extra_details=node,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to start {service_name} at {public_ip}\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def _start_service(self, manager, nodes: list, service_name: str, **kwargs):

        self.stdout(f"Starting {service_name} service...")
        for node in nodes:
            self._start_node(manager, node, service_name, **kwargs)

        if kwargs.get("cluster", False) and service_name.lower() in ("redis", "mongodb"):
            try:
                if service_name.lower() == "redis":
                    manager.start_cluster(nodes, kwargs["port"])
                else:
                    manager.start_cluster(
                        nodes, kwargs["port"], kwargs["username"], kwargs["password"]
                    )
            except Exception:
                self.stdout(
                    f"\nFailed to start {service_name} cluster. Please check connectivity between nodes.\n",
                    severity=StdoutSeverity.ERROR,
                )
                raise

        self.stdout(
            dict(
                DbServiceResponse(
                    action="start",
                    status="success",
                    message=f"{service_name.capitalize()} started successfully",
                    container=manager.get_container(),
                    extra_details={"cluster": kwargs.get("cluster", False), "nodes": nodes},
                )
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    def run(self):
        self._settings.validate_configuration_file()
        for provider in self._atomdb_backend.get_active_providers():

            if isinstance(provider, MongoDBRedisBackend):
                self._start_service(
                    self._redis_container_manager,
                    self._settings.get("services.redis.nodes", []),
                    service_name="Redis",
                    port=self._settings.get("services.redis.port"),
                    cluster=self._settings.get("services.redis.cluster", False),
                )

                self._start_service(
                    self._mongodb_container_manager,
                    self._settings.get("services.mongodb.nodes", []),
                    service_name="MongoDB",
                    port=self._settings.get("services.mongodb.port"),
                    username=self._settings.get("services.mongodb.username"),
                    password=self._settings.get("services.mongodb.password"),
                    cluster=self._settings.get("services.mongodb.cluster", False),
                    cluster_key=self._settings.get("services.mongodb.cluster_secret_key"),
                )

            elif isinstance(provider, MorkMongoDBBackend):

                self._start_service(
                    self._mongodb_container_manager,
                    self._settings.get("services.mongodb.nodes", []),
                    service_name="Redis",
                    port=self._settings.get("services.mongodb.port"),
                    username=self._settings.get("services.mongodb.username"),
                    password=self._settings.get("services.mongodb.password"),
                    cluster=self._settings.get("services.mongodb.cluster", False),
                    cluster_key=self._settings.get("services.mongodb.cluster_secret_key"),
                )

                self._start_service(
                    self._morkdb_container_manager,
                    [{}],
                    service_name="MorkDB",
                )


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

    short_help = SHORT_HELP_DB_RESTART

    help = HELP_DB_RESTART

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

    short_help = SHORT_HELP_DB_CLI

    help = HELP_DB_CLI

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
