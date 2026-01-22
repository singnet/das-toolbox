from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
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
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.prompt_types import PortRangeType

from .query_agent_container_service_response import QueryAgentContainerServiceResponse

from .query_agent_docs import *

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
        try:
            self.stdout("Stopping Query Agent service...")
            self._query_agent_bus_manager.stop()

            success_message = "Query Agent service stopped"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    QueryAgentContainerServiceResponse(
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
            warning_message = f"The Query Agent service named {container_name} is already stopped."
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    QueryAgentContainerServiceResponse(
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
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

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
        self.stdout("Starting Query Agent service...")

        query_agent_port = self._settings.get("services.query_agent.port")

        try:
            self._bus_node_container_manager.start_container(port_range, **kwargs)

            success_message = f"Query Agent started on port {query_agent_port}"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )

            self.stdout(
                dict(
                    QueryAgentContainerServiceResponse(
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
                f"Query Agent is already running. It's listening on port {query_agent_port}"
            )

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )

            self.stdout(
                dict(
                    QueryAgentContainerServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError:
            message = (
                f"Failed to start Query Agent. Please ensure that the port {query_agent_port} is not already in use "
                "and that the required services are running."
            )
            raise DockerError(message)

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
        self._query_agent_stop.run()
        self._query_agent_start.run(port_range=port_range)


class QueryAgentCli(CommandGroup):
    name = "query-agent"

    aliases = ["qa", "query"]

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
