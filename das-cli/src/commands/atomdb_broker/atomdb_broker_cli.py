from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.exceptions import PortBindingError
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.prompt_types import PortRangeType
from common.service_response import CONTAINER_START_FAILURE_MESSAGE, ServiceResponse, StdoutStatus

from .atomdb_broker_docs import (
    HELP_ATOMDB_BROKER,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_ATOMDB_BROKER,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)

CLI_SERVICE_NAME = "atomdb_broker"


class AtomDbBrokerStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the node.",
            default="47000:47999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_START

    help = HELP_START

    @inject
    def __init__(
        self,
        atomdb_broker_bus_manager: BusNodeContainerManager,
        atomdb_backend: AtomdbBackend,
        settings: Settings,
    ):
        self._atomdb_broker_bus_manager = atomdb_broker_bus_manager
        self._atomdb_backend = atomdb_backend
        self._settings = settings
        super().__init__()

    def _get_container(self):
        return self._atomdb_broker_bus_manager.get_container()

    def _start_container(self, port_range, **kwargs):
        container = self._get_container()
        port = container.port

        self.log("Starting AtomDB Broker service...", severity=StdoutSeverity.INFO)

        try:
            self._atomdb_broker_bus_manager.start_container(port_range, **kwargs)
            message = f"AtomDB Broker started on port {port}"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=self._get_container(),
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            message = f"AtomDB Broker is already running. It's listening on port {port}"

            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.INFO,
                    message=message,
                    container=self._get_container(),
                ),
                severity=StdoutSeverity.WARNING,
            )

        except (DockerError, PortBindingError) as error:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.ERROR,
                    message=CONTAINER_START_FAILURE_MESSAGE,
                    error=error,
                    container=self._get_container(),
                ),
                severity=StdoutSeverity.ERROR,
            )

    @ensure_container_running(
        [
            "_atomdb_backend",
        ],
        exception_text="\nPlease start the required services before running 'atomdb-broker start'.\n"
        "Run 'db start' to start the databases",
        verbose=False,
    )
    def run(self, port_range, **kwargs):
        self._settings.validate_configuration_file()
        self._start_container(port_range, **kwargs)


class AtomDbBrokerStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(self, atomdb_broker_bus_manager: BusNodeContainerManager, settings: Settings):
        self._settings = settings
        self._atomdb_broker_bus_manager = atomdb_broker_bus_manager
        super().__init__()

    def _get_container(self):
        return self._atomdb_broker_bus_manager.get_container()

    def _stop_container(self):
        container = self._get_container()

        self.log("Stopping AtomDB Broker service...", severity=StdoutSeverity.INFO)

        try:
            self._atomdb_broker_bus_manager.stop()
            exec_message = "AtomDB Broker service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=container,
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._get_container().name

            message = f"The AtomDB Broker service named {container_name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=self._get_container(),
                    ),
                ),
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.validate_configuration_file()
        self._stop_container()


class AtomDbBrokerRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the node.",
            default="45000:45999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

    @inject
    def __init__(
        self, atomdb_broker_start: AtomDbBrokerStart, atomdb_broker_stop: AtomDbBrokerStop
    ):
        self._atomdb_broker_start = atomdb_broker_start
        self._atomdb_broker_stop = atomdb_broker_stop
        super().__init__()

    def run(self, port_range, **kwargs):
        self._atomdb_broker_stop.run()
        self._atomdb_broker_start.run(port_range, **kwargs)


class AtomDbBrokerCli(CommandGroup):
    name = "atomdb-broker"

    short_help = SHORT_HELP_ATOMDB_BROKER

    help = HELP_ATOMDB_BROKER

    @inject
    def __init__(
        self,
        atom_db_broker_start: AtomDbBrokerStart,
        atom_db_broker_stop: AtomDbBrokerStop,
        atom_db_broker_restart: AtomDbBrokerRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                atom_db_broker_start,
                atom_db_broker_stop,
                atom_db_broker_restart,
            ]
        )
