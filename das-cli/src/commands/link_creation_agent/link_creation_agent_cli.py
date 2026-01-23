from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.container_manager.agents.query_agent_container_manager import QueryAgentContainerManager
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError
from common.prompt_types import PortRangeType

from .lca_docs import (
    HELP_LCA,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_LCA,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)
from .link_creation_agent_container_service_response import (
    LinkCreationAgentContainerServiceResponse,
)


class LinkCreationAgentStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(
        self,
        settings: Settings,
        link_creation_bus_node_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._link_creation_agent_manager = link_creation_bus_node_manager

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
            prompt="Enter peer port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
            default="43000:43999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_START

    help = HELP_START

    @inject
    def __init__(
        self,
        settings: Settings,
        link_creation_bus_node_manager: BusNodeContainerManager,
        query_agent_container_manager: QueryAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._link_creation_bus_node_manager = link_creation_bus_node_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._link_creation_bus_node_manager.get_container()

    def _link_creation_agent(self, port_range: str, **kwargs) -> None:
        self.stdout("Starting Link Creation Agent service...")

        try:
            container = self._get_container()
            port = container.port

            self._link_creation_bus_node_manager.start_container(port_range, **kwargs)

            success_message = f"Link Creation Agent started listening on the ports {port}"
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
            warning_message = (
                f"Link Creation Agent is already running. It's listening on the ports {port}"
            )

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
    def run(self, port_range: str, **kwargs):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._link_creation_agent(port_range, **kwargs)


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
            prompt="Enter peer port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The loweer and upper bounds of the port range to be used by the command proxy.",
            default="43000:43999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

    @inject
    def __init__(
        self,
        link_creation_agent_start: LinkCreationAgentStart,
        link_creation_agent_stop: LinkCreationAgentStop,
    ) -> None:
        super().__init__()
        self._link_creation_agent_start = link_creation_agent_start
        self._link_creation_agent_stop = link_creation_agent_stop

    def run(self, port_range: str, **kwargs):
        self._link_creation_agent_stop.run()
        self._link_creation_agent_start.run(port_range, **kwargs)


class LinkCreationAgentCli(CommandGroup):
    name = "link-creation-agent"

    aliases = ["lca"]

    short_help = SHORT_HELP_LCA

    help = HELP_LCA

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
