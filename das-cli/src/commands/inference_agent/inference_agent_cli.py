from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.agents.generic_agent_containers import QueryAgentContainerManager
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.exceptions import PortBindingError
from common.prompt_types import PortRangeType
from common.service_response import CONTAINER_START_FAILURE_MESSAGE, ServiceResponse, StdoutStatus

from .inference_agent_docs import (
    HELP_INFERENCE,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_INFERENCE,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)

CLI_SERVICE_NAME = "inference_agent"


class InferenceAgentStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(
        self,
        settings: Settings,
        inference_agent_bus_node_manager: BusNodeContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_manager = inference_agent_bus_node_manager

    def _get_container(self):
        return self._inference_agent_manager.get_container()

    def _inference_agent(self):
        container = self._get_container()

        self.log("Stopping Inference Agent service...", severity=StdoutSeverity.INFO)

        try:
            self._inference_agent_manager.stop()
            exec_message = "Inference Agent service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=container,
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            message = f"The Inference Agent service named {container.name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=container,
                    )
                ),
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.validate_configuration_file()
        self._inference_agent()


class InferenceAgentStart(Command):
    name = "start"

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the command proxy.",
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
        inference_agent_bus_node_manager: BusNodeContainerManager,
        query_agent_container_manager: QueryAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_bus_node_manager = inference_agent_bus_node_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _get_container(self):
        return self._inference_agent_bus_node_manager.get_container()

    def _inference_agent(self, port_range: str) -> None:
        container = self._get_container()
        port = container.port

        self.log("Starting Inference Agent service...", severity=StdoutSeverity.INFO)

        try:
            self._inference_agent_bus_node_manager.start_container(port_range)
            message = f"Inference Agent started listening on the ports {port}"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=container,
                    )
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            message = f"Inference Agent is already running. It's listening on the ports {port}"

            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.INFO,
                    message=message,
                    container=container,
                ),
                severity=StdoutSeverity.WARNING,
            )

        except (DockerError, PortBindingError) as e:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.ERROR,
                    message=CONTAINER_START_FAILURE_MESSAGE,
                    error=e,
                    container=container,
                ),
                severity=StdoutSeverity.ERROR,
            )

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'inference-agent start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self, port_range: str):
        self._settings.validate_configuration_file()
        self._inference_agent(port_range)


class InferenceAgentRestart(Command):
    name = "restart"

    params = [
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

    def run(self, port_range: str):
        self.run_subcommand(self._inference_agent_stop)
        self.run_subcommand(self._inference_agent_start, port_range)


class InferenceAgentCli(CommandGroup):
    name = "inference-agent"

    aliases = ["ia"]

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
