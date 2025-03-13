from injector import inject

from commands.query_agent.query_agent_container_manager import QueryAgentManager
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from common import Command, CommandGroup, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerNotFoundError,
    DockerContainerDuplicateError,
    DockerError,
)

class QueryAgentStop(Command):
    name = "stop"

    short_help = "Stop the Query Agent service."

    help = """
'das-cli query-agent stop' stops the running Query Agent service.

.SH EXAMPLES

To stop a running Query Agent service:

$ das-cli query-agent stop
"""
    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_manager: QueryAgentManager,
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

        self._query_agent()


class QueryAgentStart(Command):
    name = "start"

    short_help = "Start the Query Agent service."

    help = """
'das-cli query-agent start' initializes and runs the Query Agent service.

.SH EXAMPLES

To start the Query Agent service:

$ das-cli query-agent start
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentManager,
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        attention_broker_container_manager: AttentionBrokerManager
    ) -> None:
        super().__init__()
        self._settings = settings
        self._query_agent_container_manager = query_agent_container_manager
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._attention_broker_container_manager = attention_broker_container_manager


    def _query_agent(self) -> None:
        self.stdout("Starting Query Agent service...")

        query_agent_port = self._settings.get("query_agent.port")

        try:
            self._query_agent_container_manager.start_container()

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
    def run(self):
        self._settings.raise_on_missing_file()

        self._query_agent()


class QueryAgentRestart(Command):
    name = "restart"

    short_help = "Restart the Query Agent service."

    help = """
'das-cli query-agent restart' stops and then starts the Query Agent service.

This command ensures a fresh instance of the Query Agent is running.

.SH EXAMPLES

To restart the Query Agent service:

$ das-cli query-agent restart
"""

    @inject
    def __init__(self, query_agent_start: QueryAgentStart, query_agent_stop: QueryAgentStop) -> None:
        super().__init__()
        self._query_agent_start = query_agent_start
        self._query_agent_stop = query_agent_stop

    def run(self):
        self._query_agent_stop.run()
        self._query_agent_start.run()


class QueryAgentCli(CommandGroup):
    name = "query-agent"

    short_help = "Manage the Query Agent service."

    help = """
'das-cli query-agent' provides commands to control the Query Agent service.

Use this command group to start, stop, or restart the service.

.SH COMMANDS

- start: Start the Query Agent service.
- stop: Stop the Query Agent service.
- restart: Restart the Query Agent service.
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
                query_agent_start.command,
                query_agent_stop.command,
                query_agent_restart.command,
            ]
        )
