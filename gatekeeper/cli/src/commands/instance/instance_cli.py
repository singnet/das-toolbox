from injector import inject

from common import Command, CommandGroup


class InstanceList(Command):
    name = "list"

    short_help = ""

    help = ""

    @inject
    def __init__(self) -> None:
        super().__init__()

    def _list(self):
        self.stdout("List")

    def run(self):
        self.list()


class InstanceCli(CommandGroup):
    name = "instance"

    short_help = ""

    help = ""

    @inject
    def __init__(
        self,
        instance_list: InstanceList,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                instance_list.command,
            ]
        )
