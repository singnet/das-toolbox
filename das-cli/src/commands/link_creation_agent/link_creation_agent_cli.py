from injector import inject

from commands.link_creation_agent.link_creation_agent_container_manager import (
    LinkCreationAgentContainerManager,
)
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError


class LinkCreationAgentStop(Command):
    name = "stop"

    short_help = "Stop the Link Creation Agent service."

    help = """
'das-cli link-creation-agent stop' stops the running Link Creation Agent service.

.SH EXAMPLES

To stop a running Link Creation Agent service:

$ das-cli link-creation-agent stop
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

    def _link_creation_agent(self):
        try:
            self.stdout("Stopping Link Creation Agent service...")
            self._link_creation_agent_manager.stop()
            self.stdout(
                "Link Creation Agent service stopped",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._link_creation_agent_manager.get_container().name
            self.stdout(
                f"The Link Creation Agent service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._link_creation_agent()


class LinkCreationAgentStart(Command):
    name = "start"

    short_help = "Start the Link Creation Agent service."

    help = """
'das-cli link-creation-agent start' initializes and runs the Link Creation Agent service.

.SH EXAMPLES

To start the Link Creation Agent service:

$ das-cli link-creation-agent start
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

    def _link_creation_agent(self) -> None:
        self.stdout("Starting Link Creation Agent service...")
        ports_in_use = [
            str(port)
            for port in self._link_creation_agent_container_manager.get_ports_in_use()
            if port
        ]
        ports_str = ", ".join(filter(None, ports_in_use))

        try:
            self._link_creation_agent_container_manager.start_container()

            self.stdout(
                f"Link Creation Agent started listening on the ports {ports_str}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Link Creation Agent is already running. It's listening on the ports {ports_str}",
                severity=StdoutSeverity.WARNING,
            )

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'link-creation-agent start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._link_creation_agent()


class LinkCreationAgentRestart(Command):
    name = "restart"

    short_help = "Restart the Link Creation Agent service."

    help = """
'das-cli link-creation-agent restart' stops and then starts the Link Creation Agent service.

This command ensures a fresh instance of the Link Creation Agent is running.

.SH EXAMPLES

To restart the Link Creation Agent service:

$ das-cli link-creation-agent restart
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

    def run(self):
        self._link_creation_agent_stop.run()
        self._link_creation_agent_start.run()


class LinkCreationAgentCli(CommandGroup):
    name = "link-creation-agent"

    short_help = "Manage the Link Creation Agent service."

    help = """
'das-cli link-creation-agent' provides commands to control the Link Creation Agent service.

Use this command group to start, stop, or restart the service.

.SH COMMANDS

- start: Start the Link Creation Agent service.
- stop: Stop the Link Creation Agent service.
- restart: Restart the Link Creation Agent service.
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
                link_creation_agent_start.command,
                link_creation_agent_stop.command,
                link_creation_agent_restart.command,
            ]
        )
