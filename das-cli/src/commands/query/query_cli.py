import asyncio
import json

from injector import inject

from common import Choice, Command, CommandArgument, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.service_response import ServiceResponse, StdoutStatus

from ..query_agent.query_client import TERMINAL_STATUSES, CommandRouterQueryClient
from .query_docs import HELP_QUERY, HELP_RUN, SHORT_HELP_QUERY, SHORT_HELP_RUN

CLI_SERVICE_NAME = "query"
QUERY_ATTENTION_MODE_MAP = {
    "NONE": 0,
    "HANDLES": 1,
    "HANDLES_VARIABLES": 3,
}


class QueryRun(Command):
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


class QueryCli(CommandGroup):
    name = "query"

    short_help = SHORT_HELP_QUERY
    help = HELP_QUERY

    @inject
    def __init__(self, query_run: QueryRun) -> None:
        super().__init__()
        self.add_commands([query_run])