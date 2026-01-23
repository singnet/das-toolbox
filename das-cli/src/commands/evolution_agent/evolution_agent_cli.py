from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.container_manager.agents.query_agent_container_manager import QueryAgentContainerManager
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.prompt_types import PortRangeType

from .evolution_agent_docs import (
    HELP_EVOLUTION_AGENT,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_EVOLUTION_AGENT,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)
from .evolution_agent_service_response import EvolutionAgentServiceResponse


class EvolutionAgentStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

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

    short_help = SHORT_HELP_START

    help = HELP_START

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

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

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

    short_help = SHORT_HELP_EVOLUTION_AGENT

    help = HELP_EVOLUTION_AGENT

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
