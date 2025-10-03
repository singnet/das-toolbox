from injector import inject

from commands.query_agent.query_agent_container_manager import (
    QueryAgentContainerManager,
)
from commands.context_agent.context_agent_container_manager import (
    ContextAgentContainerManager,
)
from common import (
    Command,
    CommandGroup,
    CommandOption,
    Settings,
    StdoutSeverity,
    StdoutType,
)
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
)
from common.prompt_types import PortRangeType

from .context_agent_container_service_response import (
    ContextAgentContainerServiceResponse,
)


class ContextAgentStop(Command):
    name = "stop"

    short_help = "Stop the Context Agent service."

    help = """
NAME

    stop - Stop the Context Agent service

SYNOPSIS

    das-cli context-agent stop

DESCRIPTION

    Stops the running Context Agent service.

EXAMPLES

    To stop a running Context Agent service:

    $ das-cli context-agent stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        context_agent_manager: ContextAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_agent_manager = context_agent_manager

    def _get_container(self):
        return self._context_agent_manager.get_container()

    def _context_agent(self):
        try:
            self.stdout("Stopping Context Agent service...")
            self._context_agent_manager.stop()

            success_message = "Context Agent service stopped"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    ContextAgentContainerServiceResponse(
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
                f"The Context Agent service named {container_name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    ContextAgentContainerServiceResponse(
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

        self._context_agent()


class ContextAgentStart(Command):
    name = "start"

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
            prompt="Enter peer port (e.g., 8080)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            default="46000:46999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Start the Context Agent service."

    help = """
NAME

    start - Start the Context Agent service

SYNOPSIS

    das-cli context-agent start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

DESCRIPTION

    Initializes and runs the Context Agent service.

EXAMPLES

    To start the Context Agent service:

        $ das-cli context-agent start --port-range 46000:46999 --peer-hostname localhost --peer-port 42000
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentContainerManager,
        context_agent_container_manager: ContextAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_agent_container_manager = context_agent_container_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._context_agent_container_manager.get_container()

    def _context_agent(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> None:
        self.stdout("Starting Context Agent service...")

        context_agent_port = self._settings.get("services.context_agent.port")

        try:
            self._context_agent_container_manager.start_container(
                peer_hostname,
                peer_port,
                port_range,
            )

            success_message = f"Context Agent started on port {context_agent_port}"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )

            self.stdout(
                dict(
                    ContextAgentContainerServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = f"Context Agent is already running. It's listening on port {context_agent_port}"

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )

            self.stdout(
                dict(
                    ContextAgentContainerServiceResponse(
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
        exception_text="\nPlease start the required services before running 'context-agent start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._context_agent(
            peer_hostname,
            peer_port,
            port_range,
        )


class ContextAgentRestart(Command):
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
            prompt="Enter peer port (e.g., 8080)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            default="46000:46999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Restart the Context Agent service."

    help = """
NAME

    restart - Restart the Context Agent service

SYNOPSIS

    das-cli context-agent restart [--peer-hostname <hostname>] [--peer-port <port>]  [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Context Agent service.

    This command ensures a instance of the Context Agent is running.

EXAMPLES

    To restart the Context Agent service:

        $ das-cli context-agent restart --port-range 46000:46999 --peer-hostname localhost --peer-port 42000

"""

    @inject
    def __init__(
        self,
        context_agent_start: ContextAgentStart,
        context_agent_stop: ContextAgentStop,
    ) -> None:
        super().__init__()
        self._context_agent_start = context_agent_start
        self._context_agent_stop = context_agent_stop

    def run(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> None:
        self._context_agent_stop.run()
        self._context_agent_start.run(peer_hostname, peer_port, port_range)


class ContextAgentCli(CommandGroup):
    name = "context-agent"

    aliases = ["con", "context"]

    short_help = "Manage the Context Agent service."

    help = """
NAME

    context-agent - Manage the Context Agent service

SYNOPSIS

    das-cli context-agent <command> [options]

DESCRIPTION

    Provides commands to control the Context Agent service.

    Use this command group to start, stop, or restart the service.

COMMANDS

    start

        Start the Context Agent service.

    stop

        Stop the Context Agent service.

    restart

        Restart the Context Agent service.

EXAMPLES

    Start the Context Agent service:

        $ das-cli context-agent start --port-range 46000:46999 --peer-hostname localhost --peer-port 42000

    Stop the Context Agent service:

        $ das-cli context-agent stop

    Restart the Context Agent service:

        $ das-cli context-agent restart --port-range 46000:46999 --peer-hostname localhost --peer-port 42000
"""

    @inject
    def __init__(
        self,
        context_agent_start: ContextAgentStart,
        context_agent_stop: ContextAgentStop,
        context_agent_restart: ContextAgentRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                context_agent_start,
                context_agent_stop,
                context_agent_restart,
            ]
        )
