from injector import inject

from common import Command, CommandGroup, Settings, CommandOption
from .database_adapter_server_container_manager import (
    DatabaseAdapterServerContainerManager,
)


class DbAdapterStop(Command):
    name = "stop"

    short_help = ""

    help = ""

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()

        self._settings = settings

    def run(self):
        self._settings.raise_on_missing_file()


class DbAdapterStart(Command):
    name = "start"

    short_help = ""

    help = ""

    params = [
        CommandOption(
            ["--server-name", "-s"],
            help="",
            type=str,
        ),
        CommandOption(
            ["--server-port", "-p"],
            help="",
            type=int,
        ),
        CommandOption(
            ["--server-password", "-w"],
            help="",
            type=str,
            required=False,
        ),
        CommandOption(["--client"], help="", type=bool, required=False, default=True),
        CommandOption(["--server"], help="", type=bool, required=False, default=True),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        database_adapter_server_container_manager: DatabaseAdapterServerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._database_adapter_server_container_manager = (
            database_adapter_server_container_manager
        )

    def _start_server(
        self,
        hostname: str,
        port: int,
        password: str,
    ):
        self.stdout("Starting database adapter server...")
        self._database_adapter_server_container_manager.start_container(hostname, port, password)

        self.stdout("Database adapter server is runnig on port ..")

    def _start_client(self):
        pass

    def run(
        self,
        server_name: str,
        server_port: int,
        server_password: str,
        client: bool,
        server: bool,
    ) -> None:
        self._settings.raise_on_missing_file()

        self._start_server()
        self._start_client()


class DbAdapterCli(CommandGroup):
    name = "db-adapter"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        db_adapter_start: DbAdapterStart,
        db_adapter_stop: DbAdapterStop,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                db_adapter_start.command,
                db_adapter_stop.command,
            ]
        )
