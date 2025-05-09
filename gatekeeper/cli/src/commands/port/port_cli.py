from injector import inject

from common import Command, CommandGroup, CommandOption


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

    params = [
        CommandOption(
            ["--instance-id"],
            help="",
            required=True,
            type=str,
        ),
    ]

    @inject
    def __init__(self) -> None:
        super().__init__()

    def _reserve(self, instance_id: str):
        self.stdout("reserve")

    def run(self, instance_id: str):
        self._reserve(instance_id)


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
