from injector import inject

from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.prompt_types import PortRangeType

from common.bus_node.busnode_container_manager import BusNodeContainerManager
from .evolution_agent_service_response import EvolutionAgentServiceResponse


class EvolutionAgentStop(Command):
    name = "stop"

    short_help = "Stop the running Evolution Agent service"

    help = """
NAME

    das-cli evolution-agent stop - Stop the running Evolution Agent service

SYNOPSIS

    das-cli evolution-agent stop

DESCRIPTION

    Stops the currently running Evolution Agent container. This halts the processing of messages
    and deactivates the agent until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stop the running Evolution Agent service:

        $ das-cli evolution-agent stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        bus_node_container_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._evolution_agent_bus_node_manager = bus_node_container_manager

    def _get_container(self):
        return self._evolution_agent_bus_node_manager.get_container()

    def _evolution_agent(self):
        try:
            self.stdout("Stopping Evolution Agent service...")
            self._evolution_agent_bus_node_manager.stop()

            success_message = "Evolution Agent service stopped"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    EvolutionAgentServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            container_name = self._evolution_agent_bus_node_manager.get_container().name
            warning_message = (
                f"The Evolution Agent service named {container_name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    EvolutionAgentServiceResponse(
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

        self._evolution_agent()


class EvolutionAgentStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--peer-hostname"],
            help="The address of the node to connect to.",
            prompt="Enter peer hostname (e.g., 192.168.1.100)",
            type=str,
        ),
        CommandOption(
            ["--peer-port"],
            help="The port of the node to connect to.",
            prompt="Enter peer port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the node.",
            default="45000:45999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Start the Evolution Agent service."

    help = """
NAME

    das-cli evolution-agent start - Start the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

DESCRIPTION

    Starts the Evolution Agent service in a Docker container. If the service is already running,
    a warning will be shown.

    The agent begins listening on the configured port and processes messages accordingly.

EXAMPLES

    Start the Evolution Agent service:

        $ das-cli evolution-agent start --port-range 45000:45999 --peer-hostname localhost --peer-port 40002
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentContainerManager,
        bus_node_container_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._query_agent_container_manager = query_agent_container_manager
        self._evolution_agent_bus_node_manager = bus_node_container_manager

    def _get_container(self):
        return self._evolution_agent_bus_node_manager.get_container()

    def _evolution_agent(self, port_range: str, **kwargs) -> None:
        self.stdout("Starting Evolution Agent service...")

        container = self._get_container()
        port = self._settings.get("services.evolution_agent.port")

        try:
            self._evolution_agent_bus_node_manager.start_container(port_range, **kwargs)

            success_message = f"Evolution Agent started on port {port}"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    EvolutionAgentServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = f"Evolution Agent is already running. It's listening on port {port}"

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    EvolutionAgentServiceResponse(
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
                f"Failed to start Evolution Agent. Please ensure that the port {port} is not already in use "
                "and that the required services are running."
            )
            raise DockerError(message)

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'evolution-agent start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self, port_range: str, **kwargs):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._evolution_agent(port_range, **kwargs)


class EvolutionAgentRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--peer-hostname"],
            help="The address of the peer to connect to.",
            prompt="Enter peer hostname (e.g., 192.168.1.100)",
            type=str,
        ),
        CommandOption(
            ["--peer-port"],
            help="The port of the peer to connect to.",
            prompt="Enter peer port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="45000:45999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Restart the Evolution Agent service."

    help = """
NAME

    das-cli evolution-agent restart - Restart the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent restart [--peer-hostname <hostname>] [--peer-port <port>]  [--port-range <start:end>]

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    Evolution Agent is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the Evolution Agent service:

        $ das-cli evolution-agent restart --port-range 45000:45999 --peer-hostname localhost --peer-port 40002
"""

    @inject
    def __init__(
        self,
        evolution_agent_start: EvolutionAgentStart,
        evolution_agent_stop: EvolutionAgentStop,
    ) -> None:
        super().__init__()
        self._evolution_agent_start = evolution_agent_start
        self._evolution_agent_stop = evolution_agent_stop

    def run(self, port_range: str, **kwargs):
        self._evolution_agent_stop.run()
        self._evolution_agent_start.run(port_range, **kwargs)


class EvolutionAgentCli(CommandGroup):
    name = "evolution-agent"

    aliases = ["evolution"]

    short_help = "Control the lifecycle of the Evolution Agent service."

    help = """
NAME

    das-cli evolution-agent - Manage the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the Evolution Agent service,
    which is responsible for  tracks atom importance values in different contexts and updates those values based on user queries using context-specific Hebbian networks.

COMMANDS
    start
        Start the Evolution Agent service and begin message processing.

    stop
        Stop the currently running Evolution Agent container.

    restart
        Restart the Evolution Agent container (stop followed by start).

EXAMPLES
    Start the agent:

        $ das-cli evolution-agent start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

    Stop the agent:

        $ das-cli evolution-agent stop

    Restart the agent:

        $ das-cli evolution-agent restart [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]
"""

    @inject
    def __init__(
        self,
        evolution_agent_start: EvolutionAgentStart,
        evolution_agent_stop: EvolutionAgentStop,
        evolution_agent_restart: EvolutionAgentRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                evolution_agent_start,
                evolution_agent_stop,
                evolution_agent_restart,
            ]
        )
