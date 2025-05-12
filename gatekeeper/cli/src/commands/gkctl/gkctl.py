import click
from injector import inject

from common import CommandGroup
from settings.config import VERSION


class GkCtl(CommandGroup):
    name = "gkctl"

    short_help = ""

    help = ""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self.version()

    def version(self) -> None:
        self.group = click.version_option(VERSION, message="%(prog)s %(version)s")(
            self.group
        )
