from injector import inject

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from common import Command, CommandGroup, Settings, StdoutSeverity
from common.docker.exceptions import (
    DockerContainerNotFoundError,
    DockerContainerDuplicateError,
    DockerError,
)

class AttentionBrokerStop(Command):
    name = "stop"

    short_help = "Stops the Attention Broker service."

    help = """
Stops the Attention Broker service.

This command stops the running Attention Broker container.
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        attention_broker_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._attention_broker_manager = attention_broker_manager

    def _attention_broker(self):
        try:
            self.stdout("Stopping Attention Broker service...")
            self._attention_broker_manager.stop()
            self.stdout(
                "Attention Broker service stopped",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._attention_broker_manager.get_container().name
            self.stdout(
                f"The Attention Broker service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.raise_on_missing_file()

        self._attention_broker()


class AttentionBrokerStart(Command):
    name = "start"

    short_help = "Starts the Attention Broker service."

    help = """
Starts the Attention Broker service.

This command initializes and runs the Attention Broker container.
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        attention_broker_container_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._attention_broker_container_manager = attention_broker_container_manager

    def _attention_broker(self) -> None:
        self.stdout("Starting Attention Broker service...")

        attention_broker_port = self._settings.get("attention_broker.port")

        try:
            self._attention_broker_container_manager.start_container()

            self.stdout(
                f"Attention Broker started on port {attention_broker_port}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Attention Broker is already running. It's listening on port {attention_broker_port}",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError:
            raise DockerError(
                f"\nError occurred while trying to start Attention Broker on port {attention_broker_port}\n"
            )

    def run(self):
        self._settings.raise_on_missing_file()

        self._attention_broker()


class AttentionBrokerRestart(Command):
    name = "restart"

    short_help = "Restarts the Attention Broker service."

    help = """
Restarts the Attention Broker service.

This command first stops the currently running Attention Broker container
and then starts it again, ensuring a fresh instance is running.
"""

    @inject
    def __init__(self, attention_broker_start: AttentionBrokerStart, attention_broker_stop: AttentionBrokerStop) -> None:
        super().__init__()
        self._attention_broker_start = attention_broker_start
        self._attention_broker_stop = attention_broker_stop

    def run(self):
        self._attention_broker_stop.run()
        self._attention_broker_start.run()


class AttentionBrokerCli(CommandGroup):
    name = "attention-broker"

    short_help = "Manage the Attention Broker service."

    help = """
Manage the Attention Broker service.

This command group provides controls to start, stop, and restart 
the Attention Broker service.
"""

    @inject
    def __init__(
        self,
        attention_broker_start: AttentionBrokerStart,
        attention_broker_stop: AttentionBrokerStop,
        attention_broker_restart: AttentionBrokerRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                attention_broker_start.command,
                attention_broker_stop.command,
                attention_broker_restart.command,
            ]
        )
