from injector import inject

from config.config import (
    DAS_PEER_IMAGE_NAME,
    DAS_PEER_IMAGE_VERSION,
)
from common import (
    Command,
    CommandGroup,
    Settings,
    ImageManager,
    StdoutSeverity,
)
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerNotFoundError, DockerError

from .das_peer_container_manager import DasPeerContainerManager

from commands.db.redis_container_manager import RedisContainerManager
from commands.db.mongodb_container_manager import MongodbContainerManager


class DasPeerStop(Command):
    name = "stop"

    short_help = "Stops the DAS peer server."

    help = """
'das-cli das-peer stop' stops the DAS peer server.
The DAS peer server will be shut down, halting any data receiving and processing.

After executing this command, the DAS peer server container will no longer be accessible until restarted with the 'das-cli das-peer start' command.

.SH EXAMPLES

To stop the DAS peer server:

$ das-cli das-peer stop
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
                f"The DAS Peer service has been stopped.",
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
        self._server()


class DasPeerStart(Command):
    name = "start"

    short_help = "Starts the DAS peer server."

    help = """
'das-cli das-peer start' initializes the DAS peer server.
The DAS peer server acts as the main server within this setup, receiving data and storing it in the AtomDB.

Upon starting, this command will display the port on which the DAS peer server is running.
This port can be adjusted using the 'das-cli config set' command, allowing custom network configurations.

.SH EXAMPLES

To start the DAS peer server for data collection and storage:

$ das-cli das-peer start
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

        self._image_manager.pull(
            DAS_PEER_IMAGE_NAME,
            DAS_PEER_IMAGE_VERSION,
        )

        self._start_server()


class DasPeerRestart(Command):
    name = "restart"

    short_help = "Restarts the DAS peer server."

    help = """
'das-cli das-peer restart' stops and then restarts the DAS peer server container.
This command is useful for applying configuration changes or resolving issues without manually stopping and starting the server.

.SH EXAMPLES

To restart the DAS peer server:

$ das-cli das-peer restart
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
        'das-cli dbms-adapter das-peer' commands provide control over the DAS peer server, 
        which acts as the main server in the DAS setup. 
        Using 'das-cli dbms-adapter das-peer', you can start, stop, and restart the DAS peer 
        server container as needed to manage its operations and connectivity.
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
                das_peer_start.command,
                das_peer_stop.command,
                das_peer_restart.command,
            ]
        )
