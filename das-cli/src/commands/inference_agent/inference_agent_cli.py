from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError
from common.prompt_types import PortRangeType

from .inference_agent_container_service_response import InferenceAgentContainerServiceResponse

from .inference_agent_docs import * 

class InferenceAgentStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(
        self,
        settings: Settings,
        bus_node_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_bus_node_manager = bus_node_manager

    def _get_container(self):
        return self._inference_agent_bus_node_manager.get_container()

    def _inference_agent(self):
        container = self._get_container()

        try:
            self.stdout("Stopping Inference Agent service...")
            self._inference_agent_bus_node_manager.stop()

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
            help="The address of the node to connect to.",
            prompt="Enter node hostname (e.g., 192.168.1.100)",
            type=str,
        ),
        CommandOption(
            ["--peer-port"],
            help="The port of the node to connect to.",
            prompt="Enter node port (e.g., 40002)",
            type=int,
        ),
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the node.",
            default="44000:44999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_START

    help = HELP_START

    @inject
    def __init__(
        self,
        settings: Settings,
        bus_node_container_manager: BusNodeContainerManager,
        attention_broker_container_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_bus_node_manager = bus_node_container_manager
        self._attention_broker_container_manager = attention_broker_container_manager

    def _get_container(self):
        return self._inference_agent_bus_node_manager.get_container()

    def _inference_agent(self, port_range: str, **kwargs) -> None:
        container = self._get_container()

        self.stdout("Starting Inference Agent service...")

        inf_a_port = self._settings.get("services.inference_agent.port")

        try:
            self._inference_agent_bus_node_manager.start_container(port_range, **kwargs)

            success_message = f"Inference Agent started listening on the ports {inf_a_port}"

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
    def run(self, port_range: str, **kwargs):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._inference_agent(port_range, **kwargs)


class InferenceAgentRestart(Command):
    name = "restart"

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
            default="44000:44999",
            type=PortRangeType(),
        ),
    ]

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

    @inject
    def __init__(
        self,
        inference_agent_start: InferenceAgentStart,
        inference_agent_stop: InferenceAgentStop,
    ) -> None:
        super().__init__()
        self._inference_agent_start = inference_agent_start
        self._inference_agent_stop = inference_agent_stop

    def run(self, port_range: str, **kwargs):
        self._inference_agent_stop.run()
        self._inference_agent_start.run(port_range, **kwargs)


class InferenceAgentCli(CommandGroup):
    name = "inference-agent"

    aliases = ["inference"]

    short_help = SHORT_HELP_INFERENCE

    help = HELP_INFERENCE

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
