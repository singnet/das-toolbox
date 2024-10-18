from injector import inject

from common import Command, CommandGroup, Settings, CommandArgument
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
       CommandArgument(
           ["password"],
       ),

       CommandArgument(
           ["hostname"],
       ),

       CommandArgument(
           ["port"],
       ) 
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

    def _start_server(self):
        self.stdout("Starting database adapter server...")
        self._database_adapter_server_container_manager.start_container()

        self.stdout("Database adapter server is runnig on port ..")

    def _start_client(self):
        pass

    def run(self):
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
