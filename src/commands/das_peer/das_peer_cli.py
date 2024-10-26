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

from common.docker.exceptions import DockerContainerNotFoundError, DockerError

from .das_peer_container_manager import DasPeerContainerManager


class DasPeerStop(Command):
    name = "stop"

    short_help = ""

    help = ""

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
            container_name = self._das_peer_container_manager.get_container().get_name()
            self.stdout(
                f"The DAS Peer service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._server()


class DasPeerStart(Command):
    name = "start"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        das_peer_container_manager: DasPeerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._das_peer_container_manager = das_peer_container_manager
        self._image_manager.pull(
            DAS_PEER_IMAGE_NAME,
            DAS_PEER_IMAGE_VERSION,
        )

    def _start_server(self) -> None:
        self.stdout("Starting DAS Peer server...")
        self._das_peer_container_manager.start_container()

        adapter_server_port = self._das_peer_container_manager.get_port()
        self.stdout(
            f"DAS Peer is runnig on port {adapter_server_port}",
            severity=StdoutSeverity.SUCCESS,
        )

    def run(self) -> None:
        self._settings.raise_on_missing_file()

        self._start_server()


class DasPeerRestart(Command):
    name = "restart"

    short_help = ""

    help = ""

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

    short_help = ""

    help = ""

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
