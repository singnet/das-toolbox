from injector import inject

from commands.db.atomdb_backend import (
    AtomdbBackend,
)
from common import (
    Command,
    CommandGroup,
    CommandOption,
    Settings,
    StdoutSeverity,
    StdoutType,
)
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.prompt_types import PortRangeType

from .atomdb_broker_service_response import AtomDbBrokerServiceReponse


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

    short_help = "Starts the AtomDb Broker agent"

    help = '''
NAME

    das-cli atomdb-broker start - Start the atomdb-broker service

SYNOPSIS

    das-cli atomdb-broker start [--port-range <start:end>]

DESCRIPTION

    Starts the AtomDb Broker service in a Docker container. If the service is already running,
    a warning will be shown.

    The service begins listening on the configured port.

EXAMPLES

    Start the AtomDb Broker service:

        $ das-cli atomdb-broker start --port-range 47000:47999
'''

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
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()
        self._start_container(port_range, **kwargs)


class AtomDbBrokerStop(Command):
    name = "stop"

    short_help = "Starts the AtomDb Broker agent"

    help = '''
NAME

    das-cli atomdb-broker stop - Stop the AtomDB Broker service

SYNOPSIS

    das-cli atomdb-broker stop

DESCRIPTION

    Stops the currently running AtomDB Broker container. This halts the processing of messages
    and deactivates the service until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stops the AtomDb Broker service:

        $ das-cli atomdb-broker stop
'''

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
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

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

    short_help = "Restart the AtomDB Broker service."

    help = """
NAME

    das-cli atomdb-broker restart - Restart the AtomDB Broker service

SYNOPSIS

    das-cli atomdb-broker restart

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    AtomDB Broker is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the AtomDB Broker service:

        $ das-cli atomdb-broker restart
"""

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

    short_help = "Control the lifecycle of the AtomDB Broker service."

    help = """
NAME

    das-cli atomdb-broker - Manage the AtomDB Broker service

SYNOPSIS

    das-cli atomdb-broker [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the AtomDB Broker service,

COMMANDS
    start
        Start the AtomDB Broker service and begin message processing.

    stop
        Stop the currently running AtomDB Broker container.

    restart
        Restart the AtomDB Broker container (stop followed by start).

EXAMPLES
    Start the broker:

        $ das-cli atomdb-broker start

    Stop the broker:

        $ das-cli atomdb-broker stop

    Restart the broker:

        $ das-cli atomdb-broker restart
"""

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
