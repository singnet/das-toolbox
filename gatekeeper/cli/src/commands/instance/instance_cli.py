from injector import inject

from common import Command, CommandGroup, StdoutSeverity
from common.exceptions import InstanceAlreadyJoinedError
from .instance_service import InstanceService


class InstanceJoin(Command):
    name = "join"

    short_help = ""

    help = ""

    @inject
    def __init__(self, instance_service: InstanceService) -> None:
        super().__init__()
        self._instance_service = instance_service

    def _display_instance(self, result: dict) -> None:
        self.stdout(f"ID: {result['id']}", severity=StdoutSeverity.INFO)
        self.stdout(f"Name: {result['name']}\n", severity=StdoutSeverity.INFO)

        meta = result.get("meta", {})
        self.stdout("📦 System Metadata:", severity=StdoutSeverity.INFO)
        self.stdout(f"  - Architecture:   {meta.get('architecture', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - CPU Count:      {meta.get('cpu_count', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - Hostname:       {meta.get('hostname', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - Node:           {meta.get('node', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - OS:             {meta.get('os', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - OS Release:     {meta.get('os_release', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - OS Version:     {meta.get('os_version', 'N/A')}", severity=StdoutSeverity.INFO)
        self.stdout(f"  - Processor:      {meta.get('processor', 'N/A')}", severity=StdoutSeverity.INFO)


    def run(self):
        try:
            result = self._instance_service.join()

            self.stdout("Instance successfully joined!\n", severity=StdoutSeverity.INFO)

            self._display_instance(result)

        except InstanceAlreadyJoinedError as e:
            self.stdout('Instance has already been joined.', severity=StdoutSeverity.ERROR)
        except Exception as e:
            self.stdout(str(e), severity=StdoutSeverity.ERROR)


class InstanceList(Command):
    name = "list"

    short_help = ""

    help = ""

    @inject
    def __init__(self, instance_service: InstanceService) -> None:
        super().__init__()
        self._instance_service = instance_service

    def _display_instances(self, results: list[dict]) -> None:
        if not results:
            self.stdout("No instances found.", severity=StdoutSeverity.WARNING)
            return

        for result in results:
            self.stdout(f"\n🔹 ID: {result['id']}", severity=StdoutSeverity.INFO)
            self.stdout(f"🔸 Name: {result['name']}", severity=StdoutSeverity.INFO)

            meta = result.get("meta", {})
            self.stdout("📦 System Metadata:", severity=StdoutSeverity.INFO)
            self.stdout(f"  - Architecture:   {meta.get('architecture', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - CPU Count:      {meta.get('cpu_count', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - Hostname:       {meta.get('hostname', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - Node:           {meta.get('node', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - OS:             {meta.get('os', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - OS Release:     {meta.get('os_release', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - OS Version:     {meta.get('os_version', 'N/A')}", severity=StdoutSeverity.INFO)
            self.stdout(f"  - Processor:      {meta.get('processor', 'N/A')}", severity=StdoutSeverity.INFO)


    def run(self):
        result = self._instance_service.list()

        self._display_instances(result)



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
