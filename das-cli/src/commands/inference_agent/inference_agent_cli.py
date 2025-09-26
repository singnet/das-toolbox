from injector import inject

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from commands.inference_agent.inference_agent_container_manager import (
    InferenceAgentContainerManager,
)
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError
from common.prompt_types import PortRangeType

from .inference_agent_container_service_response import InferenceAgentContainerServiceResponse


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

    def _get_container(self):
        return self._inference_agent_manager.get_container()

    def _inference_agent(self):
        container = self._get_container()

        try:
            self.stdout("Stopping Inference Agent service...")
            self._inference_agent_manager.stop()

            success_message = "Inference Agent service stopped"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    InferenceAgentContainerServiceResponse(
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
                f"The Inference Agent service named {container.name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    InferenceAgentContainerServiceResponse(
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

        self._inference_agent()


class InferenceAgentStart(Command):
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
            default="44000:44999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Start the Inference Agent service."

    help = """
NAME

    inference-agent start - Start the Inference Agent service

SYNOPSIS

    das-cli inference-agent start [--peer-hostname <hostname>] [--peer-port <port>] [--port-range <start:end>]

DESCRIPTION

    Starts the Inference Agent service, initializing the required containers and ports.
    Checks that dependent services (e.g., Attention Broker) are running before starting.
    Shows the ports on which the service is listening.

EXAMPLES

    To start the Inference Agent service:

        das-cli inference-agent start --peer-hostname localhost --peer-port 8080 --port-range 5000:5100
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        inference_agent_container_manager: InferenceAgentContainerManager,
        attention_broker_container_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_container_manager = inference_agent_container_manager
        self._attention_broker_container_manager = attention_broker_container_manager

    def _get_container(self):
        return self._inference_agent_container_manager.get_container()

    def _inference_agent(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> None:
        container = self._get_container()

        self.stdout("Starting Inference Agent service...")

        try:
            self._inference_agent_container_manager.start_container(
                peer_hostname,
                peer_port,
                port_range,
            )

            success_message = f"Inference Agent started listening on the ports {container.port}"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    InferenceAgentContainerServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = (
                f"Inference Agent is already running. It's listening on the ports {container.port}"
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    InferenceAgentContainerServiceResponse(
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
            "_attention_broker_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'inference-agent start'.\n"
        "Run 'attention-broker start' to start the Attention Broker.",
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
            default="44000:44999",
            type=PortRangeType(),
        ),
    ]

    short_help = "Restart the Inference Agent service."

    help = """
NAME

    inference-agent restart - Restart the Inference Agent service

SYNOPSIS

    das-cli inference-agent restart [--peer-hostname <hostname>] [--peer-port <port>] [--port-range <start:end>]

DESCRIPTION

    Stops the running Inference Agent service and then starts it again.
    Useful for applying changes or recovering the service state.

EXAMPLES

    To restart the Inference Agent service:

        das-cli inference-agent restart --peer-hostname localhost --peer-port 8080 --port-range 5000:5100
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

    def run(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ):
        self._inference_agent_stop.run()
        self._inference_agent_start.run(
            peer_hostname,
            peer_port,
            port_range,
        )


class InferenceAgentCli(CommandGroup):
    name = "inference-agent"

    aliases = ["inference"]

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
                inference_agent_start,
                inference_agent_stop,
                inference_agent_restart,
            ]
        )
