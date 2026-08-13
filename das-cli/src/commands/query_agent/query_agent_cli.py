from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
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

from .query_agent_docs import (
    HELP_QA,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_QA,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)

CLI_SERVICE_NAME = "query_agent"


class QueryAgentStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_bus_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._query_agent_bus_manager = query_agent_bus_manager

    def _get_container(self):
        return self._query_agent_bus_manager.get_container()

    def _query_agent(self):
        container = self._get_container()

        self.log("Stopping Query Agent service...", severity=StdoutSeverity.INFO)

        try:
            self._query_agent_bus_manager.stop()
            exec_message = "Query Agent service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=container,
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            message = f"The Query Agent service named {container.name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=container,
                    )
                ),
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.validate_configuration_file()
        self._query_agent()


class QueryAgentStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="42000:42999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_START

    help = HELP_START

    @inject
    def __init__(
        self,
        settings: Settings,
        BusNodeContainerManager: BusNodeContainerManager,
        AttentionBrokerManager: AttentionBrokerManager,
        AtomDbBackend: AtomdbBackend,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._bus_node_container_manager = BusNodeContainerManager
        self._attention_broker_manager = AttentionBrokerManager
        self._atomdb_backend = AtomDbBackend

    def _get_container(self):
        return self._bus_node_container_manager.get_container()

    def _query_engine_node(self, port_range: str, **kwargs) -> None:
        container = self._get_container()
        port = container.port

        self.log("Starting Query Agent service...", severity=StdoutSeverity.INFO)

        try:
            self._bus_node_container_manager.start_container(port_range, **kwargs)
            message = f"Query Agent started on port {port}"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=container,
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            message = f"Query Agent is already running. It's listening on port {port}"

            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.INFO,
                    message=message,
                    container=container,
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
                    container=container,
                ),
                severity=StdoutSeverity.ERROR,
            )

    @ensure_container_running(
        [
            "_atomdb_backend",
            "_attention_broker_manager",
        ],
        exception_text="\nPlease start the required services before running 'query-agent start'.\n"
        "Run 'db start' to start the databases and 'attention-broker start' to start the Attention Broker.",
        verbose=False,
    )
    def run(self, port_range: str, **kwargs) -> None:
        self._settings.validate_configuration_file()
        self._query_engine_node(port_range, **kwargs)


class QueryAgentRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="42000:42999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

    @inject
    def __init__(
        self,
        query_agent_start: QueryAgentStart,
        query_agent_stop: QueryAgentStop,
    ) -> None:
        super().__init__()
        self._query_agent_start = query_agent_start
        self._query_agent_stop = query_agent_stop

    def run(self, port_range: str):
        self.run_subcommand(self._query_agent_stop)
        self.run_subcommand(self._query_agent_start, port_range=port_range)


class QueryAgentCli(CommandGroup):
    name = "query-agent"

    aliases = ["qa", "query", "query-engine", "qe"]

    short_help = SHORT_HELP_QA
    help = HELP_QA

    @inject
    def __init__(
        self,
        query_agent_start: QueryAgentStart,
        query_agent_stop: QueryAgentStop,
        query_agent_restart: QueryAgentRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                query_agent_start,
                query_agent_stop,
                query_agent_restart,
            ]
        )
