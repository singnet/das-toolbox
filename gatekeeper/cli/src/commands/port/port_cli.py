from injector import inject

from common import Command, CommandGroup


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


class PortCli(CommandGroup):
    name = "port"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        port_release: PortRelease,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                port_release.command,
            ]
        )
