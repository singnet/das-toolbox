from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.busnode_container_manager import (
    BusNodeContainerManager,
)
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.prompt_types import PortRangeType
from common.service_response import ServiceResponse, StdoutStatus

from .command_router_docs import (
    HELP_COMMAND_ROUTER,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_COMMAND_ROUTER,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)

CLI_SERVICE_NAME = "command_router"


class CommandRouterStart(Command):
    name = "start"

    short_help = SHORT_HELP_START
    help = HELP_START

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the node.",
            default="48000:48999",
            type=PortRangeType(),
        ),
    ]

    @inject
    def __init__(
        self,
        command_router_container_manager: BusNodeContainerManager,
        atomdb_backend: AtomdbBackend,
        settings: Settings,
    ):
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._command_router_container_manager = command_router_container_manager
        super().__init__()

    def _get_container(self):
        return self._command_router_container_manager.get_container()

    def _start_container(self, port_range):
        container = self._get_container()
        port = container.port

        self.log("Starting Command Router service...")

        try:
            self._command_router_container_manager.start_container(ports_range=port_range)
            message = f"Command Router started on port {port}"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=self._get_container(),
                    )
                ),
            )

        except DockerContainerDuplicateError:
            message = f"Command Router is already running. It's listening on port {port}"

            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.INFO,
                    message=message,
                    container=self._get_container(),
                ),
                StdoutSeverity.INFO,
            )

        except DockerError as e:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.ERROR,
                    message="DAS-CLI failed to instanciate a container of this service.",
                    error=e,
                    container=self._get_container(),
                )
            )

    @ensure_container_running(
        ["_atomdb_backend"],
        exception_text="\nPlease start the required services before running "
        "'command-router start'.\n"
        "Run 'db start' to start the databases",
        verbose=False,
    )
    def run(self, port_range):
        self._settings.validate_configuration_file()
        self._start_container(port_range)


class CommandRouterStop(Command):
    name = "stop"

    short_help = SHORT_HELP_STOP
    help = HELP_STOP

    @inject
    def __init__(
        self,
        command_router_container_manager: BusNodeContainerManager,
        settings: Settings,
    ):
        self._settings = settings
        self._command_router_container_manager = command_router_container_manager
        super().__init__()

    def _get_container(self):
        return self._command_router_container_manager.get_container()

    def _stop_container(self):
        container = self._get_container()

        self.log("Stopping Command Router service...")

        try:
            self._command_router_container_manager.stop()
            exec_message = "Command Router service stopped"

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
            )

        except DockerContainerNotFoundError:
            container_name = self._get_container().name
            message = f"The Command Router service named {container_name} is already stopped."

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
        self._stop_container()


class CommandRouterRestart(Command):
    name = "restart"
    short_help = SHORT_HELP_RESTART
    help = HELP_RESTART

    params = [
        CommandOption(
            ["--port-range"],
            help="The lower and upper bounds of the port range to be used by the node.",
            default="48000:48999",
            type=PortRangeType(),
        )
    ]

    @inject
    def __init__(
        self, command_router_start: CommandRouterStart, command_router_stop: CommandRouterStop
    ):
        self.command_router_start = command_router_start
        self.command_router_stop = command_router_stop
        super().__init__()

    def run(self, port_range):
        self.command_router_stop.run()
        self.command_router_start.run(port_range=port_range)


class CommandRouterCli(CommandGroup):
    name = "command-router"

    short_help = SHORT_HELP_COMMAND_ROUTER
    help = HELP_COMMAND_ROUTER

    @inject
    def __init__(
        self,
        command_router_start: CommandRouterStart,
        command_router_stop: CommandRouterStop,
        command_router_restart: CommandRouterRestart,
    ):
        super().__init__()

        self.add_commands(
            [
                command_router_start,
                command_router_stop,
                command_router_restart,
            ]
        )
