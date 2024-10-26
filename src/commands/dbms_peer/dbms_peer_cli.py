from injector import inject

from common.prompt_types import AbsolutePath
from common.docker.exceptions import DockerError

from config.config import DBMS_PEER_IMAGE_NAME, DBMS_PEER_IMAGE_VERSION
from common import (
    Command,
    CommandGroup,
    Settings,
    ImageManager,
    CommandOption,
)

from .dbms_peer_container_manager import DbmsPeerContainerManager

from commands.das_peer.das_peer_container_manager import DasPeerContainerManager


class DbmsPeerRun(Command):
    name = "run"

    short_help = ""

    help = ""

    params = [
        CommandOption(
            ["--client-hostname"],
            help="",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--client-port"],
            help="",
            type=int,
            required=True,
        ),
        CommandOption(
            ["--client-username"],
            help="",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--client-password"],
            help="",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--client-database"],
            help="",
            type=str,
            default="postgres",
            required=False,
        ),
        CommandOption(
            ["--context"],
            help="",
            type=AbsolutePath(
                file_okay=True,
                dir_okay=False,
                exists=True,
                readable=True,
            ),
            required=True,
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        dbms_peer_container_manager: DbmsPeerContainerManager,
        das_peer_container_manager: DasPeerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._dbms_peer_container_manager = dbms_peer_container_manager
        self._das_peer_container_manager = das_peer_container_manager

        self._image_manager.pull(
            DBMS_PEER_IMAGE_NAME,
            DBMS_PEER_IMAGE_VERSION,
        )

    def _start_client(
        self,
        context: str,
        hostname: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ) -> None:
        self.stdout(f"Starting DBMS Peer {hostname}:{port}")

        self._dbms_peer_container_manager.start_container(
            context,
            hostname,
            port,
            username,
            password,
            database,
        )
        self.stdout("Done.")

    def _raise_on_server_not_running(self):
        is_server_running = self._das_peer_container_manager.is_running()

        if not is_server_running:
            raise DockerError(
                "The server is not running. Please start the server by executing `das-peer start` before attempting to run this command."
            )

    def run(
        self,
        context: str,
        client_hostname: str,
        client_port: int,
        client_username: str,
        client_password: str,
        client_database: str,
    ) -> None:
        self._settings.raise_on_missing_file()
        self._raise_on_server_not_running()
        self._start_client(
            context,
            client_hostname,
            client_port,
            client_username,
            client_password,
            client_database,
        )


class DbmsPeerCli(CommandGroup):
    name = "dbms-peer"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        dbms_peer_run: DbmsPeerRun,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                dbms_peer_run.command,
            ]
        )
