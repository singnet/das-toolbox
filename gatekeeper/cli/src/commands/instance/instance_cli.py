from injector import inject

from common import Command, CommandGroup, StdoutSeverity
from common.exceptions import InstanceAlreadyJoinedError
from .instance_service import InstanceService


class InstanceJoin(Command):
    name = "join"

    short_help = "Join the current machine as a managed instance."

    help = (
        "Registers the current machine as a managed instance in the system.\n\n"
        "The instance will be uniquely identified by a generated ID and its system metadata.\n"
        "After joining, this instance will be tracked by the API for port monitoring and management.\n\n"
        "Use this command only once per environment. Attempting to join again will result in an error."
    )

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

    short_help = "List all registered instances."

    help = (
        "Displays all instances that have previously joined the system.\n\n"
        "Each instance will show:\n"
        "- ID and name\n"
        "- System metadata such as architecture, CPU count, OS, and hostname.\n\n"
        "Useful for verifying registered nodes and their metadata."
    )

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

    short_help = "Manage machine instances connected to the port tracking system."

    help = (
        "This command group contains commands to manage instances that are part of the system.\n\n"
        "Available commands:\n"
        "  join   - Register the current environment as an instance.\n"
        "  list   - Show all registered instances and their metadata.\n\n"
        "Use `--help` with each command to get more details."
    )

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
