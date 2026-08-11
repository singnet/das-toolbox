from injector import inject

from common import (
    Command,
    CommandGroup,
    Settings,
    StdoutSeverity,
)
from common.container_manager.dbms.database_adapter_container_manager import (
    DatabaseAdapterContainerManager,
)
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerNotFoundError
from common.factory.atomdb.atomdb_backend import AtomdbBackend

from .database_adapter_docs import (
    HELP_DATABASE_ADAPTER,
    HELP_RUN,
    SHORT_HELP_DATABASE_ADAPTER,
    SHORT_HELP_RUN,
)


class DatabaseAdapterRun(Command):
    name = "run"

    short_help = SHORT_HELP_RUN
    help = HELP_RUN

    @inject
    def __init__(
        self,
        database_adapter_container_manager: DatabaseAdapterContainerManager,
        atomdb_backend: AtomdbBackend,
        settings: Settings,
    ):
        self._database_adapter_container_manager = database_adapter_container_manager
        self._atomdb_backend = atomdb_backend
        self._settings = settings

        super().__init__()

    @ensure_container_running(
        ["_atomdb_backend"],
        exception_text="\nPlease start the required services before running "
        "'dbms-adapter run'.\n"
        "Run 'db start' to start the databases",
        verbose=False,
    )
    def run(self):
        self._settings.validate_configuration_file()

        self.log("Starting Database Adapter...", severity=StdoutSeverity.INFO)

        try:
            self._database_adapter_container_manager.start_container()

            self.log("Database Adapter started successfully.", severity=StdoutSeverity.SUCCESS)

        except Exception as e:
            raise RuntimeError(f"Failed to start Database Adapter.\n" f"Original error: {e}")


class DatabaseAdapterStop(Command):
    name = "stop"

    short_help = "Stop the Database Adapter"
    help = "Stop the Database Adapter container."

    @inject
    def __init__(
        self,
        database_adapter_container_manager: DatabaseAdapterContainerManager,
        settings: Settings,
    ):
        self._database_adapter_container_manager = database_adapter_container_manager
        self._settings = settings

        super().__init__()

    def run(self):
        self._settings.validate_configuration_file()

        self.log("Stopping Database Adapter...", severity=StdoutSeverity.INFO)

        try:
            self._database_adapter_container_manager.stop()

            self.log("Database Adapter stopped successfully.", severity=StdoutSeverity.SUCCESS)

        except DockerContainerNotFoundError:
            container_name = self._database_adapter_container_manager.get_container().name

            self.log(
                f"The Database Adapter service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )


class DatabaseAdapterCli(CommandGroup):
    name = "database-adapter"

    aliases = ["dbms"]

    short_help = SHORT_HELP_DATABASE_ADAPTER
    help = HELP_DATABASE_ADAPTER

    @inject
    def __init__(
        self, database_adapter_run: DatabaseAdapterRun, database_adapter_stop: DatabaseAdapterStop
    ) -> None:
        super().__init__()

        self.add_commands([database_adapter_run, database_adapter_stop])
