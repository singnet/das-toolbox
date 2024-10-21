from injector import inject

from config.config import (
    DATABASE_ADAPTER_SERVER_IMAGE_NAME,
    DATABASE_ADAPTER_SERVER_IMAGE_VERSION,
)
from common import (
    Command,
    CommandGroup,
    Settings,
    CommandOption,
    ImageManager,
    StdoutSeverity,
)
from .database_adapter_server_container_manager import (
    DatabaseAdapterServerContainerManager,
)
from .database_adapter_client_container_manager import (
    DatabaseAdapterClientContainerManager,
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
        # CommandOption(
        #     ["--server-name", "-s"],
        #     help="",
        #     type=str,
        # ),
        # CommandOption(
        #     ["--server-password", "-w"],
        #     help="",
        #     type=str,
        #     required=False,
        # ),
        CommandOption(
            ["--client"],
            help="",
            type=bool,
            required=False,
            is_flag=True,
        ),
        CommandOption(
            ["--server"],
            help="",
            type=bool,
            required=False,
            is_flag=True,
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        database_adapter_server_container_manager: DatabaseAdapterServerContainerManager,
        database_adapter_client_container_manager: DatabaseAdapterClientContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._database_adapter_server_container_manager = (
            database_adapter_server_container_manager
        )
        self._database_adapter_client_container_manager = (
            database_adapter_client_container_manager
        )

        self._image_manager.pull(
            DATABASE_ADAPTER_SERVER_IMAGE_NAME,
            DATABASE_ADAPTER_SERVER_IMAGE_VERSION,
        )

    def _start_server(self):
        self.stdout("Starting database adapter server...")
        self._database_adapter_server_container_manager.start_container()

        adapter_server_port = self._database_adapter_server_container_manager.get_port()
        self.stdout(
            f"Database adapter server is runnig on port {adapter_server_port}",
            severity=StdoutSeverity.SUCCESS,
        )

    def _start_client(self, username: str, password: str):
        self.stdout("Starting database adapter client...")
        self._database_adapter_client_container_manager.start_container(
            username,
            password,
        )

    def run(
        self,
        client: bool,
        server: bool,
    ) -> None:
        self._settings.raise_on_missing_file()

        if server:
            self._start_server()

        # self._start_client()


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
