from injector import inject

from common import Command, CommandGroup, Settings, StdoutSeverity, StdoutType
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

from .attention_broker_service_response import AttentionBrokerServiceResponse


class AttentionBrokerStop(Command):
    name = "stop"

    short_help = "Stop the running Attention Broker service"

    help = """
NAME

    das-cli attention-broker stop - Stop the running Attention Broker service

SYNOPSIS

    das-cli attention-broker stop

DESCRIPTION

    Stops the currently running Attention Broker container. This halts the processing of messages
    and deactivates the broker until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stop the running Attention Broker service:

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

    def _get_container(self):
        return self._attention_broker_manager.get_container()

    def _attention_broker(self):
        try:
            self.stdout("Stopping Attention Broker service...")
            self._attention_broker_manager.stop()

            success_message = "Attention Broker service stopped"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    AttentionBrokerServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            container_name = self._attention_broker_manager.get_container().name
            warning_message = (
                f"The Attention Broker service named {container_name} is already stopped."
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    AttentionBrokerServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=self._get_container(),
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._attention_broker()


class AttentionBrokerStart(Command):
    name = "start"

    short_help = "Start the Attention Broker service."

    help = """
NAME

    das-cli attention-broker start - Start the Attention Broker service

SYNOPSIS

    das-cli attention-broker start

DESCRIPTION

    Starts the Attention Broker service in a Docker container. If the service is already running,
    a warning will be shown.

    The broker begins listening on the configured port and processes messages accordingly.

EXAMPLES

    Start the Attention Broker service:

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

    def _get_container(self):
        return self._attention_broker_container_manager.get_container()

    def _attention_broker(self) -> None:
        self.stdout("Starting Attention Broker service...")

        container = self._attention_broker_container_manager.get_container()
        ab_port = self._attention_broker_container_manager._options.get("attention_broker_port")

        try:
            self._attention_broker_container_manager.start_container()

            success_message = f"Attention Broker started on port {ab_port}"

            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    AttentionBrokerServiceResponse(
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
                f"Attention Broker is already running. It's listening on port {ab_port}"
            )

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    AttentionBrokerServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=container,
                    )
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError:
            error_message = (
                f"\nError occurred while trying to start Attention Broker on port {ab_port}\n"
            )
            raise DockerError(error_message)

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._attention_broker()


class AttentionBrokerRestart(Command):
    name = "restart"

    short_help = "Restart the Attention Broker service."

    help = """
NAME

    das-cli attention-broker restart - Restart the Attention Broker service

SYNOPSIS

    das-cli attention-broker restart

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    Attention Broker is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the Attention Broker service:

        $ das-cli attention-broker restart
"""

    @inject
    def __init__(
        self,
        attention_broker_start: AttentionBrokerStart,
        attention_broker_stop: AttentionBrokerStop,
    ) -> None:
        super().__init__()
        self._attention_broker_start = attention_broker_start
        self._attention_broker_stop = attention_broker_stop

    def run(self):
        self._attention_broker_stop.run()
        self._attention_broker_start.run()


class AttentionBrokerCli(CommandGroup):
    name = "attention-broker"

    aliases = ["ab"]

    short_help = "Control the lifecycle of the Attention Broker service."

    help = """
NAME

    das-cli attention-broker - Manage the Attention Broker service

SYNOPSIS

    das-cli attention-broker [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the Attention Broker service,
    which is responsible for  tracks atom importance values in different contexts and updates those values based on user queries using context-specific Hebbian networks.

COMMANDS
    start
        Start the Attention Broker service and begin message processing.

    stop
        Stop the currently running Attention Broker container.

    restart
        Restart the Attention Broker container (stop followed by start).

EXAMPLES
    Start the broker:

        $ das-cli attention-broker start

    Stop the broker:

        $ das-cli attention-broker stop

    Restart the broker:

        $ das-cli attention-broker restart
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
                attention_broker_start,
                attention_broker_stop,
                attention_broker_restart,
            ]
        )
