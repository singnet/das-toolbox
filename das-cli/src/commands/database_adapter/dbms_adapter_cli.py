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
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.service_response import ServiceResponse, StdoutStatus

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

            self.stdout(
                dict(
                    ServiceResponse(
                        service="database-adapter",
                        action="run",
                        status=StdoutStatus.SUCCESS,
                        message="Database Adapter started successfully.",
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except Exception as error:
            self.stdout(
                dict(
                    ServiceResponse(
                        service="database-adapter",
                        action="run",
                        status=StdoutStatus.ERROR,
                        message="Failed to start Database Adapter.",
                        error=str(error),
                    )
                ),
                severity=StdoutSeverity.ERROR,
            )
            raise


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

            self.stdout(
                dict(
                    ServiceResponse(
                        service="database-adapter",
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message="Database Adapter stopped successfully.",
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            container_name = self._database_adapter_container_manager.get_container().name

            self.stdout(
                dict(
                    ServiceResponse(
                        service="database-adapter",
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=(
                            f"The Database Adapter service named {container_name} "
                            "is already stopped."
                        ),
                    )
                ),
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
