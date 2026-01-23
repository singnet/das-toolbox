from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.container_manager.agents.generic_agent_containers import QueryAgentContainerManager
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError
from common.prompt_types import PortRangeType

from .context_broker_container_service_response import ContextBrokerContainerServiceResponse
from .context_broker_docs import (
    HELP_CONTEXT_BROKER,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_CONTEXT_BROKER,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)


class ContextBrokerStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(
        self, settings: Settings, context_broker_bus_node_manager: BusNodeContainerManager
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_broker_bus_node_manager = context_broker_bus_node_manager

    def _get_container(self):
        return self._context_broker_bus_node_manager.get_container()

    def _context_broker(self):
        try:
            self.stdout("Stopping Context Broker service...")
            self._context_broker_bus_node_manager.stop()

            success_message = "Context Broker service stopped"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            container_name = self._get_container().name
            warning_message = (
                f"The Context Broker service named {container_name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.validate_configuration_file()
        self._context_broker()


class ContextBrokerStart(Command):
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
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="46000:46999",
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
        context_broker_bus_node_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_broker_bus_node_manager = context_broker_bus_node_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._context_broker_bus_node_manager.get_container()

    def _context_broker(self, port_range: str, **kwargs) -> None:
        self.stdout("Starting Context Broker service...")

        context_broker_port = self._settings.get("services.context_broker.port")

        try:
            self._context_broker_bus_node_manager.start_container(port_range, **kwargs)

            success_message = f"Context Broker started on port {context_broker_port}"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )

            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = (
                f"Context Broker is already running. It's listening on port {context_broker_port}"
            )

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )

            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'context-broker start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self, port_range: str, **kwargs) -> None:
        self._settings.validate_configuration_file()
        self._context_broker(port_range, **kwargs)


class ContextBrokerRestart(Command):
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
            default="46000:46999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

    @inject
    def __init__(
        self,
        context_broker_start: ContextBrokerStart,
        context_broker_stop: ContextBrokerStop,
    ) -> None:
        super().__init__()
        self._context_broker_start = context_broker_start
        self._context_broker_stop = context_broker_stop

    def run(self, port_range: str, **kwargs) -> None:
        self._context_broker_stop.run()
        self._context_broker_start.run(port_range, **kwargs)


class ContextBrokerCli(CommandGroup):
    name = "context-broker"

    aliases = ["con", "context"]

    short_help = SHORT_HELP_CONTEXT_BROKER

    help = HELP_CONTEXT_BROKER

    @inject
    def __init__(
        self,
        context_broker_start: ContextBrokerStart,
        context_broker_stop: ContextBrokerStop,
        context_broker_restart: ContextBrokerRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                context_broker_start,
                context_broker_stop,
                context_broker_restart,
            ]
        )
