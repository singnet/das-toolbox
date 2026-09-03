import asyncio
import json

from injector import inject

from common import Choice, Command, CommandArgument, CommandGroup, CommandOption, Settings, StdoutSeverity
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

from .query_client import TERMINAL_STATUSES, CommandRouterQueryClient
from .query_agent_docs import (
    HELP_QA,
    HELP_RESTART,
    HELP_RUN,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_QA,
    SHORT_HELP_RESTART,
    SHORT_HELP_RUN,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)

CLI_SERVICE_NAME = "query_agent"
QUERY_ATTENTION_MODE_MAP = {
    "NONE": 0,
    "HANDLES": 1,
    "HANDLES_VARIABLES": 3,
}


class QueryAgentRun(Command):
    name = "run"

    short_help = SHORT_HELP_RUN
    help = HELP_RUN

    params = [
        CommandArgument(
            ["query_text"],
            type=str,
        ),
        CommandOption(
            ["--attention-correlation"],
            type=Choice(list(QUERY_ATTENTION_MODE_MAP.keys())),
            required=False,
            default=None,
            help="Configure attention_correlation (NONE, HANDLES, HANDLES_VARIABLES).",
        ),
        CommandOption(
            ["--attention-update"],
            type=Choice(list(QUERY_ATTENTION_MODE_MAP.keys())),
            required=False,
            default=None,
            help="Configure attention_update (NONE, HANDLES, HANDLES_VARIABLES).",
        ),
        CommandOption(
            ["--unique-assignment"],
            type=Choice(["true", "false"]),
            required=False,
            default=None,
            help="Set unique_assignment_flag for this query execution.",
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        command_router_query_client: CommandRouterQueryClient,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._command_router_query_client = command_router_query_client

    def _build_query_params(
        self,
        attention_correlation: str | None,
        attention_update: str | None,
        unique_assignment: str | None,
    ) -> dict:
        params = {}

        if attention_correlation is not None:
            params["attention_correlation"] = QUERY_ATTENTION_MODE_MAP[attention_correlation]

        if attention_update is not None:
            params["attention_update"] = QUERY_ATTENTION_MODE_MAP[attention_update]

        if unique_assignment is not None:
            params["unique_assignment_flag"] = unique_assignment.lower() == "true"

        return params

    def _render_chunk(self, event: dict) -> None:
        answers = event.get("data")
        if not isinstance(answers, list):
            return

        for answer in answers:
            if isinstance(answer, dict):
                self.stdout(json.dumps(answer), new_line=True)
                continue

            self.stdout(str(answer), new_line=True)

    async def _stream_execution(self, execution_id: str) -> str:
        last_status = "completed"

        async for event in self._command_router_query_client.stream_events(execution_id):
            if self.output_format == "plain":
                event_type = event.get("type")
                if event_type == "chunk":
                    self._render_chunk(event)
                    continue

                status = event.get("status")
                if status in TERMINAL_STATUSES:
                    last_status = status
                    details = event.get("message")
                    if details:
                        self.log(details, severity=StdoutSeverity.INFO)
                continue

            self.stdout(event)
            status = event.get("status")
            if status in TERMINAL_STATUSES:
                last_status = status

        return last_status

    def run(
        self,
        query_text: str,
        attention_correlation: str | None = None,
        attention_update: str | None = None,
        unique_assignment: str | None = None,
    ) -> None:
        self._settings.validate_configuration_file()

        parameters = self._build_query_params(
            attention_correlation=attention_correlation,
            attention_update=attention_update,
            unique_assignment=unique_assignment,
        )

        response_payload = self._command_router_query_client.create_execution(
            query_text=query_text,
            parameters=parameters or None,
        )

        response_params = response_payload.get("params", {})
        execution_id = (
            response_payload.get("execution_id")
            or response_payload.get("id")
            or (response_params.get("execution_id") if isinstance(response_params, dict) else None)
        )
        if not execution_id:
            raise RuntimeError(
                "Command-router did not return an execution identifier for the query request."
            )

        self.log(f"Streaming execution {execution_id}...", severity=StdoutSeverity.INFO)

        terminal_status = asyncio.run(self._stream_execution(execution_id))

        if terminal_status in {"error", "aborted"}:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="run",
                    status=StdoutStatus.ERROR,
                    message=(
                        f"Query execution {execution_id} finished with status '{terminal_status}'."
                    ),
                ),
                severity=StdoutSeverity.ERROR,
            )
            return

        self.stdout(
            ServiceResponse(
                service=CLI_SERVICE_NAME,
                action="run",
                status=StdoutStatus.SUCCESS,
                message=f"Query execution {execution_id} completed successfully.",
            ),
            severity=StdoutSeverity.SUCCESS,
        )


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
        query_agent_run: QueryAgentRun,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                query_agent_start,
                query_agent_stop,
                query_agent_restart,
                query_agent_run,
            ]
        )
