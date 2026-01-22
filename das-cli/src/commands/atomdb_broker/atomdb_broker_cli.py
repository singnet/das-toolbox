from injector import inject

from common import (
    Command,
    CommandGroup,
    CommandOption,
    Settings,
    StdoutSeverity,
    StdoutType,
)
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)
from common.prompt_types import PortRangeType

from .atomdb_broker_service_response import AtomDbBrokerServiceReponse

from .atomdb_broker_docs import *

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

        self.stdout("Starting AtomDB Broker service...")

        try:
            self._atomdb_broker_bus_manager.start_container(port_range, **kwargs)
            message = f"AtomDB Broker started on port {port}"

            self.stdout(message, severity=StdoutSeverity.SUCCESS)

            self.stdout(
                dict(
                    AtomDbBrokerServiceReponse(
                        action="start",
                        status="success",
                        message=message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        except DockerContainerDuplicateError:
            message = f"AtomDB Broker is already running. It's listening on port {port}"

            self.stdout(message, severity=StdoutSeverity.WARNING)

            self.stdout(
                dict(
                    AtomDbBrokerServiceReponse(
                        action="start",
                        status="already_running",
                        message=message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

        except DockerError:
            message = (
                f"Failed to start AtomDB Broker. Please ensure that the port {port} is not already in use "
                "and that the required services are running."
            )

            raise DockerError(message)

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

        self.stdout("Stopping AtomDB Broker service...")

        try:
            self._atomdb_broker_bus_manager.stop()
            exec_message = "AtomDB Broker service stopped"

            self.stdout(exec_message, severity=StdoutSeverity.SUCCESS)

            self.stdout(
                dict(
                    AtomDbBrokerServiceReponse(
                        action="stop",
                        status="already_stopped",
                        message=exec_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            container_name = self._get_container().name

            message = f"The AtomDB Broker service named {container_name} is already stopped."

            self.stdout(message, severity=StdoutSeverity.WARNING)

            self.stdout(
                dict(
                    AtomDbBrokerServiceReponse(
                        action="stop",
                        status="already_stopped",
                        message=message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
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

    short_help = HELP_RESTART

    help = SHORT_HELP_RESTART

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
