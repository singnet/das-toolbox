from injector import inject

from commands.context_broker.context_broker_container_manager import ContextBrokerContainerManager
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError
from common.prompt_types import PortRangeType

from .context_broker_container_service_response import ContextBrokerContainerServiceResponse

from commands.bus_node.busnode_container_manager import BusNodeContainerManager

class ContextBrokerStop(Command):
    name = "stop"

    short_help = "Stop the Context Broker service."

    help = """
NAME

    stop - Stop the Context Broker service

SYNOPSIS

    das-cli context-broker stop

DESCRIPTION

    Stops the running Context Broker service.

EXAMPLES

    To stop a running Context Broker service:

    $ das-cli context-broker stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        context_broker_bus_node_manager: BusNodeContainerManager
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_broker_bus_node_manager = context_broker_bus_node_manager

    def _get_container(self):
        return self._context_broker_bus_node_manager.get_container()

    def _context_broker(self):
        try:
            self.stdout("Stopping Context Broker service...")
            self._context_broker_bus_node_manager.stop()

            success_message = "Context Broker service stopped"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
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
                f"The Context Broker service named {container_name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
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

        self._context_broker()


class ContextBrokerStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--peer-hostname"],
            help="The address of the node to connect to.",
            prompt="Enter peer hostname (e.g., 192.168.1.100)",
            type=str,
        ),
        CommandOption(
            ["--peer-port"],
            help="The port of the node to connect to.",
            prompt="Enter peer port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="46000:46999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Start the Context Broker service."

    help = """
NAME

    start - Start the Context Broker service

SYNOPSIS

    das-cli context-broker start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

DESCRIPTION

    Initializes and runs the Context Broker service.

EXAMPLES

    To start the Context Broker service:

        $ das-cli context-broker start --port-range 46000:46999 --peer-hostname localhost --peer-port 42000
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentContainerManager,
        context_broker_bus_node_manager: BusNodeContainerManager
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_broker_bus_node_manager = context_broker_bus_node_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._context_broker_bus_node_manager.get_container()

    def _context_broker(
        self,
        port_range: str,
        **kwargs
    ) -> None:
        self.stdout("Starting Context Broker service...")

        context_broker_port = self._settings.get("services.context_broker.port")

        try:
            self._context_broker_bus_node_manager.start_container(
                port_range,
                **kwargs
            )

            success_message = f"Context Broker started on port {context_broker_port}"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )

            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
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
                f"Context Broker is already running. It's listening on port {context_broker_port}"
            )

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )

            self.stdout(
                dict(
                    ContextBrokerContainerServiceResponse(
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
        exception_text="\nPlease start the required services before running 'context-broker start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(
        self,
        port_range: str,
        **kwargs
    ) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._context_broker(
            port_range,
            **kwargs
        )


class ContextBrokerRestart(Command):
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
            prompt="Enter peer port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="46000:46999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Restart the Context Broker service."

    help = """
NAME

    restart - Restart the Context Broker service

SYNOPSIS

    das-cli context-broker restart [--peer-hostname <hostname>] [--peer-port <port>]  [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Context Broker service.

    This command ensures a instance of the Context Broker is running.

EXAMPLES

    To restart the Context Broker service:

        $ das-cli context-broker restart --port-range 46000:46999 --peer-hostname localhost --peer-port 42000

"""

    @inject
    def __init__(
        self,
        context_broker_start: ContextBrokerStart,
        context_broker_stop: ContextBrokerStop,
    ) -> None:
        super().__init__()
        self._context_broker_start = context_broker_start
        self._context_broker_stop = context_broker_stop

    def run(
        self,
        port_range: str,
        **kwargs
    ) -> None:
        self._context_broker_stop.run()
        self._context_broker_start.run(port_range, **kwargs)


class ContextBrokerCli(CommandGroup):
    name = "context-broker"

    aliases = ["con", "context"]

    short_help = "Manage the Context Broker service."

    help = """
NAME

    context-broker - Manage the Context Broker service

SYNOPSIS

    das-cli context-broker <command> [options]

DESCRIPTION

    Provides commands to control the Context Broker service.

    Use this command group to start, stop, or restart the service.

COMMANDS

    start

        Start the Context Broker service.

    stop

        Stop the Context Broker service.

    restart

        Restart the Context Broker service.

EXAMPLES

    Start the Context Broker service:

        $ das-cli context-broker start --port-range 46000:46999 --peer-hostname localhost --peer-port 42000

    Stop the Context Broker service:

        $ das-cli context-broker stop

    Restart the Context Broker service:

        $ das-cli context-broker restart --port-range 46000:46999 --peer-hostname localhost --peer-port 42000
"""

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
