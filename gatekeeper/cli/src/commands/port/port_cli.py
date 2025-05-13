from injector import inject

from common import Command, CommandGroup, StdoutSeverity, CommandOption
from common.exceptions import InstanceNotRegisteredError, InvalidRequestError
from .port_service import PortService


class PortRelease(Command):
    name = "release"

    short_help = ""

    help = ""

    params = [
        CommandOption(
            ["--port", "-p"],
            help="",
            type=int,
            required=True,
        )
    ]

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def run(self, port: int):
        try:
            result = self._port_service.release(port_number=port)

            port_number = result["port"]["port_number"]

            self.stdout(
                f"Successfully released port {port_number}",
                severity=StdoutSeverity.SUCCESS,
            )
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortReserve(Command):
    name = "reserve"

    short_help = ""

    help = ""

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def run(self):
        try:
            result = self._port_service.reserve()

            port_number = result["port"]["port_number"]

            self.stdout(
                f"Reserved port {port_number}",
                severity=StdoutSeverity.SUCCESS,
            )
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortCli(CommandGroup):
    name = "port"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        port_release: PortRelease,
        port_reserve: PortReserve,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                port_release.command,
                port_reserve.command,
            ]
        )
