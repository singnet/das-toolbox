from injector import inject

from commands.link_creation_agent.link_creation_agent_container_manager import (
    LinkCreationAgentContainerManager,
)
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError

from .link_creation_agent_container_service_response import (
    LinkCreationAgentContainerServiceResponse,
)


class LinkCreationAgentStop(Command):
    name = "stop"

    short_help = "Stop the Link Creation Agent service."

    help = """
NAME

    link-creation-agent stop - Stop the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent stop

DESCRIPTION

    Stops the running Link Creation Agent service container.
    If the service is already stopped, a warning is shown.

EXAMPLES

    To stop a running Link Creation Agent service:

        das-cli link-creation-agent stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        link_creation_agent_manager: LinkCreationAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._link_creation_agent_manager = link_creation_agent_manager

    def _get_container(self):
        return self._link_creation_agent_manager.get_container()

    def _link_creation_agent(self):
        container = self._get_container()

        try:
            self.stdout("Stopping Link Creation Agent service...")
            self._link_creation_agent_manager.stop()

            success_message = "Link Creation Agent service stopped"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    LinkCreationAgentContainerServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            warning_message = (
                f"The Link Creation Agent service named {container.name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    LinkCreationAgentContainerServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._link_creation_agent()


class LinkCreationAgentStart(Command):
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
            type=str,
            default="43000:43999",
        ),
    ]

    short_help = "Start the Link Creation Agent service."

    help = """
NAME

    link-creation-agent start - Start the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent start [--peer-hostname <hostname>] [--peer-port <port>]
    [--port-range <start_port-end_port>]

DESCRIPTION

    Initializes and runs the Link Creation Agent service.
    This command starts the service container and reports the ports where it is listening.
    Ensure the required dependent services (like Query Agent) are running before starting.

EXAMPLES

    To start the Link Creation Agent service:

        das-cli link-creation-agent start --peer-hostname localhost --peer-port 5000 --port-range 6000:6010
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        link_creation_agent_container_manager: LinkCreationAgentContainerManager,
        query_agent_container_manager: QueryAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._link_creation_agent_container_manager = link_creation_agent_container_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._link_creation_agent_container_manager.get_container()

    def _link_creation_agent(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> None:
        self.stdout("Starting Link Creation Agent service...")

        try:
            container = self._get_container()

            self._link_creation_agent_container_manager.start_container(
                peer_hostname,
                peer_port,
                port_range,
            )

            success_message = f"Link Creation Agent started listening on the ports {container.port}"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    LinkCreationAgentContainerServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=container,
                    ),
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = f"Link Creation Agent is already running. It's listening on the ports {container.port}"

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    LinkCreationAgentContainerServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'link-creation-agent start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._link_creation_agent(
            peer_hostname,
            peer_port,
            port_range,
        )


class LinkCreationAgentRestart(Command):
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
            type=str,
            default="43000:43999",
        ),
    ]

    short_help = "Restart the Link Creation Agent service."

    help = """
NAME

    link-creation-agent restart - Restart the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent restart [--peer-hostname <hostname>] [--peer-port <port>]
    [--port-range <start_port-end_port>]

DESCRIPTION

    Stops the currently running Link Creation Agent service and then starts a fresh instance.
    Useful for refreshing the service or applying configuration changes.

EXAMPLES

    To restart the Link Creation Agent service:

        das-cli link-creation-agent restart --peer-hostname localhost --peer-port 5000 --port-range 6000:6010
"""

    @inject
    def __init__(
        self,
        link_creation_agent_start: LinkCreationAgentStart,
        link_creation_agent_stop: LinkCreationAgentStop,
    ) -> None:
        super().__init__()
        self._link_creation_agent_start = link_creation_agent_start
        self._link_creation_agent_stop = link_creation_agent_stop

    def run(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ):
        self._link_creation_agent_stop.run()
        self._link_creation_agent_start.run(
            peer_hostname,
            peer_port,
            port_range,
        )


class LinkCreationAgentCli(CommandGroup):
    name = "link-creation-agent"

    aliases = ["lca"]

    short_help = "Manage the Link Creation Agent service."

    help = """
NAME

    link-creation-agent - Manage the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent <command> [options]

DESCRIPTION

    Provides commands to control the Link Creation Agent service lifecycle.
    Use this command group to start, stop, or restart the service.

COMMANDS

    start       Start the Link Creation Agent service.
    stop        Stop the Link Creation Agent service.
    restart     Restart the Link Creation Agent service.

EXAMPLES

    Start the service:

        das-cli link-creation-agent start --peer-hostname localhost --peer-port 5000 --port-range 6000:6010

    Stop the service:

        das-cli link-creation-agent stop

    Restart the service:

        das-cli link-creation-agent restart --peer-hostname localhost --peer-port 5000 --port-range 6000:6010
"""

    @inject
    def __init__(
        self,
        link_creation_agent_start: LinkCreationAgentStart,
        link_creation_agent_stop: LinkCreationAgentStop,
        link_creation_agent_restart: LinkCreationAgentRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                link_creation_agent_start,
                link_creation_agent_stop,
                link_creation_agent_restart,
            ]
        )
