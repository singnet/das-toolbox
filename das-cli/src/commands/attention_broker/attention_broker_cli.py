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

from .attention_broker_docs import (
    HELP_ATTENTION_BROKER,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_ATTENTION_BROKER,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)
from .attention_broker_service_response import AttentionBrokerServiceResponse


class AttentionBrokerStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

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
        self._settings.validate_configuration_file()
        self._attention_broker()


class AttentionBrokerStart(Command):
    name = "start"

    short_help = SHORT_HELP_START

    help = HELP_START

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
        port = container.port

        try:
            self._attention_broker_container_manager.start_container()

            success_message = f"Attention Broker started on port {port}"

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
                f"Attention Broker is already running. It's listening on port {port}"
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
                f"\nError occurred while trying to start Attention Broker on port {port}\n"
            )
            raise DockerError(error_message)

    def run(self):
        self._settings.validate_configuration_file()
        self._attention_broker()


class AttentionBrokerRestart(Command):
    name = "restart"

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

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

    short_help = SHORT_HELP_ATTENTION_BROKER

    help = HELP_ATTENTION_BROKER

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
