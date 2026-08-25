from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.vault_container_manager import VaultContainerManager
from common.docker.exceptions import (
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

    def _unseal(self, unseal_keys: list[str]) -> None:
        for key in unseal_keys:
            status = self._vault_container_manager.unseal(key)
            if not status.get("sealed", True):
                return

        if self._vault_container_manager.get_status().get("sealed", True):
            raise DockerError("Failed to unseal Vault with the provided keys.")

    def _initialize(self) -> dict:
        self.log("Initializing Vault...")
        credentials = self._vault_container_manager.initialize()
        self._confirm_secrets_stored(credentials)
        self.log("Unsealing Vault...")
        self._unseal(credentials["unseal_keys"])
        return credentials

    def _unseal_interactively(self) -> None:
        self.log("Vault is sealed. Enter the unseal keys you stored earlier.")

        while True:
            status = self._vault_container_manager.get_status()
            if not status.get("sealed", True):
                return

            progress = status.get("progress", 0)
            threshold = status.get("t", 0)
            key = Command.prompt(
                f"Unseal key ({progress}/{threshold})",
                hide_input=True,
            ).strip()
            if not key:
                continue

            try:
                status = self._vault_container_manager.unseal(key)
            except DockerError as error:
                self.log(str(error), severity=StdoutSeverity.ERROR)
                continue

            if not status.get("sealed", True):
                return

            remaining = status.get("t", threshold) - status.get("progress", 0)
            self.log(f"Key accepted. {remaining} more key(s) required.")

    def _confirm_secrets_stored(self, credentials: dict) -> None:
        for index, key in enumerate(credentials["unseal_keys"], start=1):
            self.log(f"Unseal Key {index}: {key}", severity=StdoutSeverity.WARNING)
        self.log(f"Root Token: {credentials['root_token']}", severity=StdoutSeverity.WARNING)

        stored = Command.confirm(
            "Have you stored the unseal keys and root token in a safe place",
            default=True,
        )
        if not stored:
            self.log(
                "Without these keys you will not be able to unseal Vault again.",
                severity=StdoutSeverity.WARNING,
            )

    def run(self):
        self._settings.validate_configuration_file()

        container = self._get_container()
        port = container.port

        self.log("Starting Vault...", severity=StdoutSeverity.INFO)

        try:
            already_running = self._vault_container_manager.is_running()
            if already_running:
                self._vault_container_manager.wait_for_api()
            else:
                self._vault_container_manager.start_container()

            status = self._vault_container_manager.get_status()
            if status.get("initialized") and not status.get("sealed") and already_running:
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
                return

            if not status.get("initialized"):
                self._initialize()
            elif status.get("sealed"):
                self._unseal_interactively()

            dashboard_url = f"http://localhost:{port}/ui"
            message = (
                f"Vault started on port {port}.\n"
                f"Open the dashboard at {dashboard_url} and use the Root Token to log in."
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
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
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

    params = [
        CommandOption(
            ["--prune", "-p"],
            is_flag=True,
            help="Remove the Vault data volume.",
            default=False,
            required=False,
        ),
    ]

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

    def run(self, prune: bool = False):
        self._settings.validate_configuration_file()

        container = self._get_container()

        self.log("Stopping Vault...", severity=StdoutSeverity.INFO)

        try:
            self._vault_container_manager.stop(remove_volume=prune)
            exec_message = "Vault service stopped"
            if prune:
                exec_message += " and data volume removed"

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
            if prune:
                message += " Data volume removed."

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
