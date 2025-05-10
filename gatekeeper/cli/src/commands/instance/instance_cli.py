from injector import inject

from common import Command, CommandGroup, StdoutSeverity
from .instance_service import InstanceService


class InstanceJoin(Command):
    name = "join"

    short_help = ""

    help = ""

    @inject
    def __init__(self, instance_service: InstanceService) -> None:
        super().__init__()
        self._instance_service = instance_service

    def run(self):
        try:
            self._instance_service.join()
        except Exception as e:
            self.stdout(
                str(e),
                severity=StdoutSeverity.ERROR,
            )


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
        instance_join: InstanceJoin,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                instance_list.command,
                instance_join.command,
            ]
        )
