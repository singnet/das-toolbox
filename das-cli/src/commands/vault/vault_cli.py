from injector import inject

from common import Command, CommandGroup, Settings, StdoutSeverity
from common.container_manager.vault_container_manager import VaultContainerManager
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.exceptions import PortBindingError
from common.service_response import CONTAINER_START_FAILURE_MESSAGE, ServiceResponse, StdoutStatus

from .vault_docs import (
    HELP_START,
    HELP_STOP,
    HELP_VAULT,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
    SHORT_HELP_VAULT,
)

CLI_SERVICE_NAME = "vault"


class VaultStart(Command):
    name = "start"

    short_help = SHORT_HELP_START

    help = HELP_START

    @inject
    def __init__(
        self,
        settings: Settings,
        vault_container_manager: VaultContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._vault_container_manager = vault_container_manager

    def _get_container(self):
        return self._vault_container_manager.get_container()

    def run(self):
        self._settings.validate_configuration_file()

        container = self._get_container()
        port = container.port

        self.log("Starting Vault...", severity=StdoutSeverity.INFO)

        try:
            admin_password = self._vault_container_manager.start_container()
            dashboard_url = f"http://localhost:{port}/ui"
            message = (
                f"Vault started on port {port}.\n"
                f"Open the dashboard at {dashboard_url} "
                f"and log in with the admin password: {admin_password}"
            )

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=container,
                        dashboard_url=dashboard_url,
                        admin_password=admin_password,
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            message = f"Vault is already running. It's listening on port {port}"

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


class VaultStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

    @inject
    def __init__(
        self,
        settings: Settings,
        vault_container_manager: VaultContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._vault_container_manager = vault_container_manager

    def _get_container(self):
        return self._vault_container_manager.get_container()

    def run(self):
        self._settings.validate_configuration_file()

        container = self._get_container()

        self.log("Stopping Vault...", severity=StdoutSeverity.INFO)

        try:
            self._vault_container_manager.stop()
            exec_message = "Vault service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=container,
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            message = f"The Vault service named {container.name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=container,
                    ),
                ),
                severity=StdoutSeverity.WARNING,
            )


class VaultCli(CommandGroup):
    name = "vault"

    short_help = SHORT_HELP_VAULT

    help = HELP_VAULT

    @inject
    def __init__(
        self,
        vault_start: VaultStart,
        vault_stop: VaultStop,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                vault_start,
                vault_stop,
            ]
        )
