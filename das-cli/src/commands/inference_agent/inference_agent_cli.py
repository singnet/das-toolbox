from injector import inject

from commands.inference_agent.inference_agent_container_manager import (
    InferenceAgentContainerManager,
)
from commands.link_creation_agent.link_creation_agent_container_manager import (
    LinkCreationAgentContainerManager,
)
from common import Command, CommandGroup, Settings, StdoutSeverity, CommandOption
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
)


class InferenceAgentStop(Command):
    name = "stop"

    short_help = "Stop the Inference Agent service."

    help = """
NAME

    inference-agent stop - Stop the Inference Agent service

SYNOPSIS

    das-cli inference-agent stop

DESCRIPTION

    Stops the running Inference Agent service.
    If the service is not running, a warning is shown.

EXAMPLES

    To stop the Inference Agent service:

        das-cli inference-agent stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        inference_agent_manager: InferenceAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_manager = inference_agent_manager

    def _inference_agent(self):
        try:
            self.stdout("Stopping Inference Agent service...")
            self._inference_agent_manager.stop()
            self.stdout(
                "Inference Agent service stopped",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._inference_agent_manager.get_container().name
            self.stdout(
                f"The Inference Agent service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._inference_agent()


class InferenceAgentStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--peer-hostname"],
            help="",
            required=True,
            type=str,
        ),
        CommandOption(
            ["--peer-port"],
            help="",
            required=True,
            type=int,
        ),
        CommandOption(
            ["--range-port"],
            help="",
            required=True,
            type=str,
        ),
    ]

    short_help = "Start the Inference Agent service."

    help = """
NAME

    inference-agent start - Start the Inference Agent service

SYNOPSIS

    das-cli inference-agent start

DESCRIPTION

    Starts the Inference Agent service, initializing the required containers and ports.
    Checks that dependent services (e.g., Link Creation Agent) are running before starting.
    Shows the ports on which the service is listening.

EXAMPLES

    To start the Inference Agent service:

        das-cli inference-agent start
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        inference_agent_container_manager: InferenceAgentContainerManager,
        link_creation_container_manager: LinkCreationAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_container_manager = inference_agent_container_manager
        self._link_creation_container_manager = link_creation_container_manager

    def _inference_agent(
        self,
        peer_address: str,
        port_range: str,
    ) -> None:
        self.stdout("Starting Inference Agent service...")
        ports_in_use = [
            str(port)
            for port in self._inference_agent_container_manager.get_ports_in_use()
            if port
        ]
        ports_str = ", ".join(filter(None, ports_in_use))

        try:
            self._inference_agent_container_manager.start_container(
                peer_address,
                port_range,
            )

            self.stdout(
                f"Inference Agent started listening on the ports {ports_str}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Inference Agent is already running. It's listening on the ports {ports_str}",
                severity=StdoutSeverity.WARNING,
            )

    @ensure_container_running(
        [
            "_link_creation_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'inference-agent start'.\n"
        "Run 'link-creation-agent start' to start the Link Creation Agent.",
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

        self._inference_agent(
            peer_hostname,
            peer_port,
            port_range,
        )


class InferenceAgentRestart(Command):
    name = "restart"

    short_help = "Restart the Inference Agent service."

    help = """
NAME

    inference-agent restart - Restart the Inference Agent service

SYNOPSIS

    das-cli inference-agent restart

DESCRIPTION

    Stops the running Inference Agent service and then starts it again.
    Useful for applying changes or recovering the service state.

EXAMPLES

    To restart the Inference Agent service:

        das-cli inference-agent restart
"""

    @inject
    def __init__(
        self,
        inference_agent_start: InferenceAgentStart,
        inference_agent_stop: InferenceAgentStop,
    ) -> None:
        super().__init__()
        self._inference_agent_start = inference_agent_start
        self._inference_agent_stop = inference_agent_stop

    def run(self):
        self._inference_agent_stop.run()
        self._inference_agent_start.run()


class InferenceAgentCli(CommandGroup):
    name = "inference-agent"

    short_help = "Manage the Inference Agent service."

    help = """
NAME

    inference-agent - Commands to manage the Inference Agent service

SYNOPSIS

    das-cli inference-agent <command>

DESCRIPTION

    Provides commands to start, stop, and restart the Inference Agent service.

COMMANDS

    start       Start the Inference Agent service.
    stop        Stop the Inference Agent service.
    restart     Restart the Inference Agent service.

EXAMPLES

    Start the service:

        das-cli inference-agent start

    Stop the service:

        das-cli inference-agent stop

    Restart the service:

        das-cli inference-agent restart
"""

    @inject
    def __init__(
        self,
        inference_agent_start: InferenceAgentStart,
        inference_agent_stop: InferenceAgentStop,
        inference_agent_restart: InferenceAgentRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                inference_agent_start.command,
                inference_agent_stop.command,
                inference_agent_restart.command,
            ]
        )
