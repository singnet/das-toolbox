from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.agents.generic_agent_containers import QueryAgentContainerManager
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.exceptions import PortBindingError
from common.prompt_types import PortRangeType
from common.service_response import ServiceResponse, StdoutStatus, CONTAINER_START_FAILURE_MESSAGE

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

CLI_SERVICE_NAME = "context_broker"


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
        self.log("Stopping Context Broker service...", severity=StdoutSeverity.INFO)

        try:
            self._context_broker_bus_node_manager.stop()
            exec_message = "Context Broker service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=self._get_container(),
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            container_name = self._get_container().name
            message = f"The Context Broker service named {container_name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=self._get_container(),
                    )
                ),
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.validate_configuration_file()
        self._context_broker()


class ContextBrokerStart(Command):
    name = "start"

    params = [
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

    def _context_broker(self, port_range: str) -> None:
        container = self._get_container()
        port = container.port

        self.log("Starting Context Broker service...", severity=StdoutSeverity.INFO)

        try:
            self._context_broker_bus_node_manager.start_container(port_range)
            message = f"Context Broker started on port {port}"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=self._get_container(),
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            message = f"Context Broker is already running. It's listening on port {port}"

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

        except (DockerError, PortBindingError) as e:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.ERROR,
                    message=CONTAINER_START_FAILURE_MESSAGE,
                    error=e,
                    container=self._get_container(),
                ),
                severity=StdoutSeverity.ERROR,
            )

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'context-broker start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self, port_range: str) -> None:
        self._settings.validate_configuration_file()
        self._context_broker(port_range)


class ContextBrokerRestart(Command):
    name = "restart"

    params = [
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

    def run(self, port_range: str) -> None:
        self._context_broker_stop.run()
        self._context_broker_start.run(port_range)


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
