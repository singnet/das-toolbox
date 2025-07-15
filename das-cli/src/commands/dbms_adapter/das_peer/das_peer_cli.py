from injector import inject

from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import Command, CommandGroup, ImageManager, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerNotFoundError
from settings.config import DAS_PEER_IMAGE_NAME, DAS_PEER_IMAGE_VERSION

from .das_peer_container_manager import DasPeerContainerManager


class DasPeerStop(Command):
    name = "stop"

    short_help = "Stops the DAS peer server."

    help = """
NAME

    das-cli dbms-adapter das-peer stop - Stop the DAS peer server container.

SYNOPSIS

    das-cli das-peer stop

DESCRIPTION

    Stop the running DAS peer server container. This will halt any data ingestion
    and disable the peer server until it is manually restarted using the start command.

    If the container is already stopped, a warning will be shown.

EXAMPLES

    das-cli dbms-adapter das-peer stop

        Stop the DAS peer server container.
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        das_peer_container_manager: DasPeerContainerManager,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._das_peer_container_manager = das_peer_container_manager

    def _server(self):
        self.stdout("Stopping DAS Peer service...")

        try:
            self._das_peer_container_manager.stop()

            self.stdout(
                "The DAS Peer service has been stopped.",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._das_peer_container_manager.get_container().name
            self.stdout(
                f"The DAS Peer service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()
        self._server()


class DasPeerStart(Command):
    name = "start"

    short_help = "Starts the DAS peer server."

    help = """
NAME

    das-cli dbms-adapter das-peer start - Start the DAS peer server container.

SYNOPSIS

    das-cli dbms-adapter das-peer start

DESCRIPTION

    Start the DAS peer server, which acts as the main server within this setup,
    responsible for receiving and storing data in the AtomDB.

    This command will ensure that all required services (MongoDB, Redis) are running
    before attempting to start the peer server. The port on which the server is running
    will be displayed upon success.

    Configuration for ports and other environment settings can be adjusted using
    the 'das-cli config' command group.

EXAMPLES

    das-cli dbms-adapter das-peer start

        Start the DAS peer server container locally.
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        das_peer_container_manager: DasPeerContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager

        self._das_peer_container_manager = das_peer_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._redis_container_manager = redis_container_manager

    def _start_server(self) -> None:
        self.stdout("Starting DAS Peer server...")
        self._das_peer_container_manager.start_container()

        adapter_server_port = self._das_peer_container_manager.get_container().port
        self.stdout(
            f"DAS Peer is runnig on port {adapter_server_port}",
            severity=StdoutSeverity.SUCCESS,
        )

    @ensure_container_running(
        ["_mongodb_container_manager", "_redis_container_manager"],
        exception_text="\nPlease use 'db start' to start required services before running 'das-peer start'.",
    )
    def run(self) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._image_manager.pull(
            DAS_PEER_IMAGE_NAME,
            DAS_PEER_IMAGE_VERSION,
        )

        self._start_server()


class DasPeerRestart(Command):
    name = "restart"

    short_help = "Restarts the DAS peer server."

    help = """
NAME

    das-cli dbms-adapter das-peer restart - Restart the DAS peer server container.

SYNOPSIS

    das-cli dbms-adapter das-peer restart

DESCRIPTION

    Stop and then start the DAS peer server container. This is useful for applying
    configuration changes, updating the environment, or recovering from unexpected issues.

    This command is functionally equivalent to running 'das-cli das-peer stop' followed
    by 'das-cli das-peer start'.

EXAMPLES

    das-cli dbms-adapter das-peer restart

        Restart the DAS peer server container to apply new configuration.
"""

    @inject
    def __init__(
        self,
        das_peer_start: DasPeerStart,
        das_peer_stop: DasPeerStop,
    ) -> None:
        super().__init__()
        self._das_peer_start = das_peer_start
        self._das_peer_stop = das_peer_stop

    def run(self):
        self._das_peer_stop.run()
        self._das_peer_start.run()


class DasPeerCli(CommandGroup):
    name = "das-peer"

    short_help = "Manage DAS peer server operations."

    help = """
NAME

    das-cli dbms-adapter das-peer - Manage operations of the DAS peer server.

SYNOPSIS

    das-cli dbms-adapter das-peer <command> [options]

DESCRIPTION

    Manage the DAS peer server container, which serves as the main component
    in the DAS setup responsible for receiving and storing data in the AtomDB.

    This command group allows you to start, stop, and restart the DAS peer
    server container as part of managing the overall DAS infrastructure.

COMMANDS

    start       Start the DAS peer server container.
    stop        Stop the DAS peer server container.
    restart     Restart the DAS peer server container.

EXAMPLES

    das-cli dbms-adapter das-peer start

        Start the DAS peer server to begin data ingestion and storage.

    das-cli dbms-adapter das-peer stop

        Stop the currently running DAS peer server container.

    das-cli dbms-adapter das-peer restart

        Restart the DAS peer server to reload configuration or recover from issues.
"""

    @inject
    def __init__(
        self,
        das_peer_start: DasPeerStart,
        das_peer_stop: DasPeerStop,
        das_peer_restart: DasPeerRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                das_peer_start,
                das_peer_stop,
                das_peer_restart,
            ]
        )
