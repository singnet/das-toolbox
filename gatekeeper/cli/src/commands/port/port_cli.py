from injector import inject

from common import Command, CommandGroup, StdoutSeverity
from common.exceptions import InstanceNotRegisteredError, InvalidRequestError
from .port_service import PortService


class PortRelease(Command):
    name = "release"

    short_help = ""

    help = ""

    @inject
    def __init__(self) -> None:
        super().__init__()

    def _release(self):
        self.stdout("Release")

    def run(self):
        self._release()


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
            self._port_service.reserve()
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
