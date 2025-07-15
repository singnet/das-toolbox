from injector import inject

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)


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

    def _query_agent(self):
        try:
            self.stdout("Stopping Query Agent service...")
            self._query_agent_manager.stop()
            self.stdout(
                "Query Agent service stopped",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._query_agent_manager.get_container().name
            self.stdout(
                f"The Query Agent service named {container_name} is already stopped.",
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
            required=True,
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

    def _query_agent(self, port_range: str) -> None:
        self.stdout("Starting Query Agent service...")

        query_agent_port = self._settings.get("services.query_agent.port")

        try:
            self._query_agent_container_manager.start_container(port_range)

            self.stdout(
                f"Query Agent started on port {query_agent_port}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Query Agent is already running. It's listening on port {query_agent_port}",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError:
            raise DockerError(
                f"\nError occurred while trying to start Query Agent on port {query_agent_port}\n"
            )

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
            required=True,
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
