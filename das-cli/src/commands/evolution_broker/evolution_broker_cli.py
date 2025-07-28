from injector import inject

from commands.evolution_broker.evolution_broker_container_manager import EvolutionBrokerManager
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

from .evolution_broker_service_response import EvolutionBrokerServiceResponse


class EvolutionBrokerStop(Command):
    name = "stop"

    short_help = "Stop the running Evolution Broker service"

    help = """
NAME

    das-cli evolution-broker stop - Stop the running Evolution Broker service

SYNOPSIS

    das-cli evolution-broker stop

DESCRIPTION

    Stops the currently running Evolution Broker container. This halts the processing of messages
    and deactivates the broker until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stop the running Evolution Broker service:

        $ das-cli evolution-broker stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        evolution_broker_manager: EvolutionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._evolution_broker_manager = evolution_broker_manager

    def _get_container(self):
        return self._evolution_broker_manager.get_container()

    def _evolution_broker(self):
        try:
            self.stdout("Stopping Evolution Broker service...")
            self._evolution_broker_manager.stop()

            success_message = "Evolution Broker service stopped"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    EvolutionBrokerServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            container_name = self._evolution_broker_manager.get_container().name
            warning_message = (
                f"The Evolution Broker service named {container_name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    EvolutionBrokerServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._evolution_broker()


class EvolutionBrokerStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--port-range"],
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            prompt="Enter port range (e.g., 3000:3010)",
            type=str,
        ),
    ]

    short_help = "Start the Evolution Broker service."

    help = """
NAME

    das-cli evolution-broker start - Start the Evolution Broker service

SYNOPSIS

    das-cli evolution-broker start [--port-range <start:end>]

DESCRIPTION

    Starts the Evolution Broker service in a Docker container. If the service is already running,
    a warning will be shown.

    The broker begins listening on the configured port and processes messages accordingly.

EXAMPLES

    Start the Evolution Broker service:

        $ das-cli evolution-broker start --port-range 8000:8100
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentContainerManager,
        evolution_broker_container_manager: EvolutionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._evolution_broker_container_manager = evolution_broker_container_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._evolution_broker_container_manager.get_container()

    def _evolution_broker(self, port_range: str) -> None:
        self.stdout("Starting Evolution Broker service...")

        container = self._get_container()
        evolution_broker_port = container.port

        try:
            self._evolution_broker_container_manager.start_container(port_range)

            success_message = f"Evolution Broker started on port {evolution_broker_port}"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    EvolutionBrokerServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = f"Evolution Broker is already running. It's listening on port {evolution_broker_port}"

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    EvolutionBrokerServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError:
            message = (
                f"Failed to start Evolution Broker. Please ensure that the port {evolution_broker_port} is not already in use "
                "and that the required services are running."
            )
            raise DockerError(message)

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'evolution-broker start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self, port_range: str):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._evolution_broker(port_range)


class EvolutionBrokerRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--port-range"],
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            prompt="Enter port range (e.g., 3000:3010)",
            type=str,
        ),
    ]

    short_help = "Restart the Evolution Broker service."

    help = """
NAME

    das-cli evolution-broker restart - Restart the Evolution Broker service

SYNOPSIS

    das-cli evolution-broker restart [--port-range <start:end>]

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    Evolution Broker is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the Evolution Broker service:

        $ das-cli evolution-broker restart --port-range 8000:8100
"""

    @inject
    def __init__(
        self,
        evolution_broker_start: EvolutionBrokerStart,
        evolution_broker_stop: EvolutionBrokerStop,
    ) -> None:
        super().__init__()
        self._evolution_broker_start = evolution_broker_start
        self._evolution_broker_stop = evolution_broker_stop

    def run(self, port_range: str):
        self._evolution_broker_stop.run()
        self._evolution_broker_start.run(port_range)


class EvolutionBrokerCli(CommandGroup):
    name = "evolution-broker"

    aliases = ["eb"]

    short_help = "Control the lifecycle of the Evolution Broker service."

    help = """
NAME

    das-cli evolution-broker - Manage the Evolution Broker service

SYNOPSIS

    das-cli evolution-broker [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the Evolution Broker service,
    which is responsible for  tracks atom importance values in different contexts and updates those values based on user queries using context-specific Hebbian networks.

COMMANDS
    start
        Start the Evolution Broker service and begin message processing.

    stop
        Stop the currently running Evolution Broker container.

    restart
        Restart the Evolution Broker container (stop followed by start).

EXAMPLES
    Start the broker:

        $ das-cli evolution-broker start [--port-range <start:end>]

    Stop the broker:

        $ das-cli evolution-broker stop

    Restart the broker:

        $ das-cli evolution-broker restart [--port-range <start:end>]
"""

    @inject
    def __init__(
        self,
        evolution_broker_start: EvolutionBrokerStart,
        evolution_broker_stop: EvolutionBrokerStop,
        evolution_broker_restart: EvolutionBrokerRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                evolution_broker_start,
                evolution_broker_stop,
                evolution_broker_restart,
            ]
        )
