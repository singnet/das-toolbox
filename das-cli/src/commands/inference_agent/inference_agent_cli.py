from injector import inject

from commands.inference_agent.inference_agent_container_manager import (
    InferenceAgentContainerManager,
)
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Command, CommandGroup, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError


class InferenceAgentStop(Command):
    name = "stop"

    short_help = "Stop the Inference Agent service."

    help = """
'das-cli inference-agent stop' stops the running Inference Agent service.

.SH EXAMPLES

To stop a running Inference Agent service:

$ das-cli inference-agent stop
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

        self._inference_agent()


class InferenceAgentStart(Command):
    name = "start"

    short_help = "Start the Inference Agent service."

    help = """
'das-cli inference-agent start' initializes and runs the Inference Agent service.

.SH EXAMPLES

To start the Inference Agent service:

$ das-cli inference-agent start
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        inference_agent_container_manager: InferenceAgentContainerManager,
        query_agent_container_manager: QueryAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_container_manager = inference_agent_container_manager
        self._query_agent_container_manager = query_agent_container_manager

    def _inference_agent(self) -> None:
        self.stdout("Starting Inference Agent service...")

        try:
            self._inference_agent_container_manager.start_container()

            self.stdout(
                "Inference Agent started listening on the ports ",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                "Inference Agent is already running. It's listening on the ports",
                severity=StdoutSeverity.WARNING,
            )

    @ensure_container_running(
        [
            "_query_agent_container_manager",
        ],
        exception_text="\nPlease start the required services before running 'inference-agent start'.\n"
        "Run 'query-agent start' to start the Query Agent.",
        verbose=False,
    )
    def run(self):
        self._settings.raise_on_missing_file()

        self._inference_agent()


class InferenceAgentRestart(Command):
    name = "restart"

    short_help = "Restart the Inference Agent service."

    help = """
'das-cli inference-agent restart' stops and then starts the Inference Agent service.

This command ensures a fresh instance of the Inference Agent is running.

.SH EXAMPLES

To restart the Inference Agent service:

$ das-cli inference-agent restart
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
'das-cli inference-agent' provides commands to control the Inference Agent service.

Use this command group to start, stop, or restart the service.

.SH COMMANDS

- start: Start the Inference Agent service.
- stop: Stop the Inference Agent service.
- restart: Restart the Inference Agent service.
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
