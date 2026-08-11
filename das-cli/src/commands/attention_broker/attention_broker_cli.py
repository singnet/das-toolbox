from injector import inject

from common import Command, CommandGroup, Settings, StdoutSeverity
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.exceptions import PortBindingError
from common.service_response import ServiceResponse, StdoutStatus

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

CLI_SERVICE_NAME = "attention_broker"


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
        self.log("Stopping Attention Broker service...")

        try:
            self._attention_broker_manager.stop()
            exec_message = "Attention Broker service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=self._get_container(),
                    )
                ),
            )

        except DockerContainerNotFoundError:
            container_name = self._attention_broker_manager.get_container().name
            message = f"The Attention Broker service named {container_name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=self._get_container(),
                    )
                ),
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
        container = self._attention_broker_container_manager.get_container()
        port = container.port

        self.log("Starting Attention Broker service...")

        try:
            self._attention_broker_container_manager.start_container()
            message = f"Attention Broker started on port {port}"

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
            )

        except DockerContainerDuplicateError:
            message = f"Attention Broker is already running. It's listening on port {port}"

            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.INFO,
                    message=message,
                    container=container,
                ),
                StdoutSeverity.INFO,
            )

        except (DockerError, PortBindingError) as e:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.ERROR,
                    message="DAS-CLI failed to instanciate a container of this service.",
                    error=e,
                    container=container,
                )
            )

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
