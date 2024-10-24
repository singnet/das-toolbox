from injector import inject

from common.prompt_types import AbsolutePath

from config.config import (
    DATABASE_ADAPTER_SERVER_IMAGE_NAME,
    DATABASE_ADAPTER_SERVER_IMAGE_VERSION,
    DATABASE_ADAPTER_CLIENT_IMAGE_NAME,
    DATABASE_ADAPTER_CLIENT_IMAGE_VERSION,
)
from common import (
    Command,
    CommandGroup,
    Settings,
    ImageManager,
    StdoutSeverity,
    CommandOption,
)

from common.docker.exceptions import DockerContainerNotFoundError, DockerError

from .database_adapter_server_container_manager import (
    DatabaseAdapterServerContainerManager,
)
from .database_adapter_client_container_manager import (
    DatabaseAdapterClientContainerManager,
)

from commands.db.redis_container_manager import RedisContainerManager
from commands.db.mongodb_container_manager import MongodbContainerManager


class DbAdapterStop(Command):
    name = "stop"

    short_help = ""

    help = ""

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

    def _server(self):
        self.stdout("Stopping Database Adapter Server service...")

        try:
            self._database_adapter_server_container_manager.stop()

            self.stdout(
                f"The Database Adapter Server service has been stopped.",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = (
                self._database_adapter_server_container_manager.get_container().get_name()
            )
            self.stdout(
                f"The Database Adapter Server service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._server()


class DbAdapterSync(Command):
    name = "sync"

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
            type=AbsolutePath(),
            required=True,
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        database_adapter_client_container_manager: DatabaseAdapterClientContainerManager,
        database_adapter_server_container_manager: DatabaseAdapterServerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._database_adapter_client_container_manager = (
            database_adapter_client_container_manager
        )
        self._database_adapter_server_container_manager = (
            database_adapter_server_container_manager
        )

        self._image_manager.pull(
            DATABASE_ADAPTER_CLIENT_IMAGE_NAME,
            DATABASE_ADAPTER_CLIENT_IMAGE_VERSION,
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
        self.stdout(f"Starting database adapter client {hostname}:{port}")

        self._database_adapter_client_container_manager.start_container(
            context,
            hostname,
            port,
            username,
            password,
            database,
        )
        self.stdout("Done.")

    def _raise_on_server_not_running(self):
        is_server_running = self._database_adapter_server_container_manager.is_running()

        if not is_server_running:
            raise DockerError(
                "The server is not running. Please start the server by executing db-adapter start before attempting to run this command."
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


class DbAdapterStart(Command):
    name = "start"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        database_adapter_server_container_manager: DatabaseAdapterServerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._database_adapter_server_container_manager = (
            database_adapter_server_container_manager
        )
        self._image_manager.pull(
            DATABASE_ADAPTER_SERVER_IMAGE_NAME,
            DATABASE_ADAPTER_SERVER_IMAGE_VERSION,
        )

    def _start_server(self) -> None:
        self.stdout("Starting database adapter server...")
        self._database_adapter_server_container_manager.start_container()

        adapter_server_port = self._database_adapter_server_container_manager.get_port()
        self.stdout(
            f"Database adapter server is runnig on port {adapter_server_port}",
            severity=StdoutSeverity.SUCCESS,
        )

    def run(self) -> None:
        self._settings.raise_on_missing_file()

        self._start_server()


class DbAdapterRestart(Command):
    name = "restart"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        db_adapter_start: DbAdapterStart,
        db_adapter_stop: DbAdapterStop,
    ) -> None:
        super().__init__()
        self._db_adapter_start = db_adapter_start
        self._db_adapter_stop = db_adapter_stop

    def run(self):
        self._db_adapter_stop.run()
        self._db_adapter_start.run()


class DbAdapterCli(CommandGroup):
    name = "db-adapter"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        db_adapter_start: DbAdapterStart,
        db_adapter_stop: DbAdapterStop,
        db_adapter_restart: DbAdapterRestart,
        db_adapter_sync: DbAdapterSync,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                db_adapter_start.command,
                db_adapter_stop.command,
                db_adapter_restart.command,
                db_adapter_sync.command,
            ]
        )
