from injector import inject

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

from .query_agent_container_service_response import QueryAgentContainerServiceResponse


class QueryAgentStop(Command):
    name = "stop"

    short_help = "Stop the Query Agent service."

    help = """
NAME

    stop - Stop the Query Agent service

SYNOPSIS

    das-cli query-agent stop

DESCRIPTION

    Stops the running Query Agent service.

EXAMPLES

    To stop a running Query Agent service:

    $ das-cli query-agent stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_manager: QueryAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._query_agent_manager = query_agent_manager

    def _get_container(self):
        return self._query_agent_manager.get_container()

    def _query_agent(self):
        try:
            self.stdout("Stopping Query Agent service...")
            self._query_agent_manager.stop()

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
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            prompt="Enter port range (e.g., 3000:3010)",
            type=str,
        ),
    ]

    short_help = "Start the Query Agent service."

    help = """
NAME

    start - Start the Query Agent service

SYNOPSIS

    das-cli query-agent start [--port-range <start:end>]

DESCRIPTION

    Initializes and runs the Query Agent service.

EXAMPLES

    To start the Query Agent service:

        $ das-cli query-agent start --port-range 8000:8100
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentContainerManager,
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        attention_broker_container_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._query_agent_container_manager = query_agent_container_manager
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._attention_broker_container_manager = attention_broker_container_manager

    def _get_container(self):
        return self._query_agent_container_manager.get_container()

    def _query_agent(self, port_range: str) -> None:
        self.stdout("Starting Query Agent service...")

        query_agent_port = self._settings.get("services.query_agent.port")

        try:
            self._query_agent_container_manager.start_container(port_range)

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
            "_mongodb_container_manager",
            "_redis_container_manager",
            "_attention_broker_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'query-agent start'.\n"
        "Run 'db start' to start the databases and 'attention-broker start' to start the Attention Broker.",
        verbose=False,
    )
    def run(self, port_range: str) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._query_agent(port_range)


class QueryAgentRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--port-range"],
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            prompt="Enter port range (e.g., 3000:3010)",
            type=str,
        ),
    ]

    short_help = "Restart the Query Agent service."

    help = """
NAME

    restart - Restart the Query Agent service

SYNOPSIS

    das-cli query-agent restart [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Query Agent service.

    This command ensures a frinstance of the Query Agent is running.

EXAMPLES

    To restart the Query Agent service:

        $ das-cli query-agent restart --port-range 8000:8100

"""

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
        self._query_agent_start.run(port_range)


class QueryAgentCli(CommandGroup):
    name = "query-agent"

    aliases = ["qa", "query"]

    short_help = "Manage the Query Agent service."

    help = """
NAME

    query-agent - Manage the Query Agent service

SYNOPSIS

    das-cli query-agent <command> [options]

DESCRIPTION

    Provides commands to control the Query Agent service.

    Use this command group to start, stop, or restart the service.

COMMANDS

    start

        Start the Query Agent service.

    stop

        Stop the Query Agent service.

    restart

        Restart the Query Agent service.

EXAMPLES

    Start the Query Agent service:

        $ das-cli query-agent start --port-range 8000:8100

    Stop the Query Agent service:

        $ das-cli query-agent stop

    Restart the Query Agent service:

        $ das-cli query-agent restart --port-range 8000:8100
"""

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
