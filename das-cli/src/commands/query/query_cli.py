import asyncio
import json
from pathlib import Path

from injector import inject

from common import Command, CommandArgument, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.service_response import ServiceResponse, StdoutStatus

from ..query_agent.query_client import TERMINAL_STATUSES, CommandRouterQueryClient
from .query_docs import HELP_QUERY, HELP_RUN, SHORT_HELP_QUERY, SHORT_HELP_RUN

CLI_SERVICE_NAME = "query"


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
            ["--public-key"],
            type=str,
            required=False,
            help="Public key file path or name; only a bare name can fall back to ~/.das.",
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

    @staticmethod
    def _get_params_section(section: object) -> dict:
        if not isinstance(section, dict):
            return {}

        params = section.get("params")
        if not isinstance(params, dict):
            return {}

        return dict(params)

    @staticmethod
    def _is_empty_param_value(value: object) -> bool:
        if value is None:
            return True

        if isinstance(value, str):
            return value.strip() == ""

        if isinstance(value, (list, tuple, dict, set)):
            return len(value) == 0

        return False

    def _build_query_params_from_config(self) -> dict:
        config = self._settings.get_content()
        if not isinstance(config, dict):
            return {}

        agents = config.get("agents")
        if not isinstance(agents, dict):
            return {}

        params = self._get_params_section(agents.get("base_query"))
        params.update(self._get_params_section(agents.get("query")))

        params.pop("public_key_tokens", None)

        return {
            key: value for key, value in params.items() if not self._is_empty_param_value(value)
        }

    def _load_public_key_tokens(self, public_key_file: str) -> str:
        if not public_key_file.strip():
            raise ValueError("Public key file name must not be empty.")

        candidates = [Path(public_key_file).expanduser()]
        if (
            Path(public_key_file).name == public_key_file
            and public_key_file not in (".", "..")
            and not public_key_file.startswith("~")
        ):
            candidates.append(Path.home() / ".das" / public_key_file)

        for candidate in candidates:
            try:
                public_key = candidate.read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                continue
            if not public_key or any(character.isspace() for character in public_key):
                raise ValueError(
                    f"Public key file must contain a single non-empty token: {candidate}"
                )
            break
        else:
            paths = ", ".join(str(candidate) for candidate in candidates)
            raise FileNotFoundError(f"Public key file not found. Checked: {paths}")

        config = self._settings.get_content()
        atomdb = config.get("atomdb") if isinstance(config, dict) else None
        uid = atomdb.get("uid") if isinstance(atomdb, dict) else None
        if not isinstance(uid, str) or not uid or any(character.isspace() for character in uid):
            raise ValueError("atomdb.uid must be a single non-empty token to use --public-key.")
        return f"{uid} {public_key}"

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
        public_key: str | None = None,
    ) -> None:
        self._settings.validate_configuration_file()

        parameters = self._build_query_params_from_config()
        if public_key is not None:
            parameters["public_key_tokens"] = self._load_public_key_tokens(public_key)

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
