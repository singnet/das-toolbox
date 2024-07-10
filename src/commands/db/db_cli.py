from injector import inject
from common import Command, CommandGroup, Settings, StdoutSeverity
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerError,
    DockerContainerNotFoundError,
)
from .mongodb_container_manager import MongodbContainerManager
from .redis_container_manager import RedisContainerManager


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
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def _redis_node(self, redis_container_name, redis_node):
        node_context = redis_node.get("context")
        node_ip = redis_node.get("ip")
        node_username = redis_node.get("username")

        try:
            redis_container_manager = RedisContainerManager(
                redis_container_name,
                exec_context=node_context,
            )

            redis_container_manager.stop()

            self.stdout(
                f"The Redis service at {node_ip} has been stopped by the {node_username} user",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            self.stdout(
                f"The Redis service named {redis_container_name} at {node_ip} is already stopped by the {node_username} user.",
                severity=StdoutSeverity.WARNING,
            )

    def _redis(self):
        self.stdout(f"Stopping redis service...")

        redis_container_name = self._settings.get("redis.container_name")
        redis_nodes = self._settings.get("redis.nodes", [])

        try:
            for redis_node in redis_nodes:
                self._redis_node(redis_container_name, redis_node)
        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to stop Redis\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def _mongodb(self):
        mongodb_container_name = self._settings.get("mongodb.container_name")

        try:
            MongodbContainerManager(mongodb_container_name).stop()

            self.stdout("MongoDB service stopped", severity=StdoutSeverity.SUCCESS)
        except DockerContainerNotFoundError:
            self.stdout(
                f"The MongoDB service named {mongodb_container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to stop MongoDB\n",
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
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def _redis_node(
        self,
        redis_container_name: str,
        redis_port: int,
        redis_node: dict,
    ):
        node_context = redis_node.get("context")
        node_ip = redis_node.get("ip")
        node_username = redis_node.get("username")

        redis_container_manager = RedisContainerManager(
            redis_container_name,
            exec_context=node_context,
        )

        try:
            redis_container_manager.start_container(redis_port)

            self.stdout(
                f"Redis has started successfully on port {redis_port} at {node_ip}, operating under the user {node_username}.",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Redis is already running. It is currently listening on port {redis_port} at IP address {node_ip} under the user {node_username}.",
                severity=StdoutSeverity.WARNING,
            )

    def _redis_cluster(
        self,
        redis_container_name: str,
        redis_nodes: list,
        redis_port: int,
    ):
        redis_container_manager = RedisContainerManager(redis_container_name)

        redis_container_manager.start_cluster(redis_nodes, redis_port)

    def _redis(self):
        self.stdout(f"Starting Redis service...")

        redis_container_name = self._settings.get("redis.container_name")
        redis_port = self._settings.get("redis.port")
        redis_nodes = self._settings.get("redis.nodes", [])
        redis_cluster = self._settings.get("redis.cluster")

        try:
            for redis_node in redis_nodes:
                self._redis_node(redis_container_name, redis_port, redis_node)

            if redis_cluster:
                self._redis_cluster(redis_container_name, redis_nodes, redis_port)

        except DockerError as e:
            cluster_text = "cluster" if redis_cluster else ""

            self.stdout(
                f"\nError occurred while trying to start Redis {cluster_text} on port {redis_port}\n",
                severity=StdoutSeverity.ERROR,
            )
            raise e

    def _mongodb_node(
        self,
        mongodb_container_name: str,
        mongodb_port: int,
        mongodb_node: dict,
    ):
        pass

    def _mongodb_cluster(
        self,
        mongodb_container_name: str,
        mongodb_nodes: list,
        mongodb_port: int,
    ):
        mongodb_container_manager = MongodbContainerManager(mongodb_container_name)

        mongodb_container_manager.start_cluster(mongodb_nodes, mongodb_port)

    def _mongodb(self):
        self.stdout(f"Starting MongoDB service...")

        mongodb_container_name = self._settings.get("mongodb.container_name")
        mongodb_port = self._settings.get("mongodb.port")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")

        try:
            mongodb_container_manager = MongodbContainerManager(mongodb_container_name)

            mongodb_container_manager.start_container(
                mongodb_port,
                mongodb_username,
                mongodb_password,
            )
            self.stdout(
                f"MongoDB started on port {mongodb_port}",
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            self.stdout(
                f"MongoDB is already running. It's listening on port {mongodb_port}",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError as e:
            self.stdout(
                f"\nError occurred while trying to start MongoDB on port {mongodb_port}\n",
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
'das-cli db restart' restarts all database containers previously started with 'das-cli start'. If no database have been started, 'das-cli db restart' just start them.

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

    help = "'das-cli db' commands allow you to manage DAS backend DBMSs for use with the DAS CLI. 'das-cli db' provides commands to start, stop, and restart the databases as needed."

    @inject
    def __init__(
        self,
        db_start: DbStart,
        db_stop: DbStop,
        db_restart: DbRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                db_start.command,
                db_stop.command,
                db_restart.command,
            ]
        )
