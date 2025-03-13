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

    short_help = "Stop the Attention Broker service."

    help = """
'das-cli attention-broker stop' stops the running Attention Broker service.

This command ensures that no further messages are processed until the service is started again.

.SH EXAMPLES

To stop a running Attention Broker service:

$ das-cli attention-broker stop
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

    short_help = "Start the Attention Broker service."

    help = """
'das-cli attention-broker start' initializes and runs the Attention Broker service.

This command starts the Attention Broker container, allowing it to begin processing messages.

.SH EXAMPLES

To start the Attention Broker service:

$ das-cli attention-broker start
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

    short_help = "Restart the Attention Broker service."

    help = """
'das-cli attention-broker restart' stops and then starts the Attention Broker service.

This command ensures a fresh instance of the Attention Broker is running.

.SH EXAMPLES

To restart the Attention Broker service:

$ das-cli attention-broker restart
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
'das-cli attention-broker' provides commands to control the Attention Broker service.

Use this command group to start, stop, or restart the service.

.SH COMMANDS

- start: Start the Attention Broker service.
- stop: Stop the Attention Broker service.
- restart: Restart the Attention Broker service.
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
