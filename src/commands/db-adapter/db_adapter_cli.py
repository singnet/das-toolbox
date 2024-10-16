from injector import inject

from common import Command, CommandGroup


class DbAdapterStop(Command):
    name = "stop"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def run(self):
        self._settings.raise_on_missing_file()


class DbAdapterStart(Command):
    name = "start"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def run(self):
        self._settings.raise_on_missing_file()


class DbAdapterCli(CommandGroup):
    name = "db-adapter"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        db_adapter_start: DbAdapterStart,
        db_adapter_stop: DbAdapterStop,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                db_adapter_start.command,
                db_adapter_stop.command,
            ]
        )
