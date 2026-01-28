from injector import inject

from common import Command, CommandGroup, Settings, StdoutType
from common.container_manager.system_containers_manager import SystemContainersManager
from common.utils import print_table

from .system_docs import HELP_STATUS, HELP_SYSTEM, SHORT_HELP_STATUS, SHORT_HELP_SYSTEM


class SystemStatus(Command):
    name = "status"

    aliases = ["st", "stat"]

    short_help = SHORT_HELP_STATUS

    help = HELP_STATUS

    @inject
    def __init__(
        self, settings: Settings, system_containers_manager: SystemContainersManager
    ) -> None:
        self._system_containers_manager = system_containers_manager
        self._settings = settings

        super().__init__()

    def _format_services_status(self, status_dict: dict) -> None:
        rows = []
        for name, info in status_dict.items():
            port = info.get("port") or "-"
            version = info.get("version", ["-"])[0] if info.get("version") else "-"
            status = info.get("status", "unknown") or "-"
            port_range = info.get("port_range") or "-"

            rows.append(
                {
                    "NAME": name,
                    "VERSION": version,
                    "STATUS": status,
                    "PORT": port,
                    "PORT RANGE": port_range,
                }
            )

        print_table(
            rows,
            columns=["NAME", "VERSION", "STATUS", "PORT", "PORT RANGE"],
            align={"NAME": "<", "VERSION": "<", "STATUS": "^", "PORT": "<", "PORT RANGE": "<"},
            stdout=self.stdout,
        )

    def run(self) -> None:
        self._settings.validate_configuration_file()

        output = self._system_containers_manager.get_services_status()

        self.stdout(
            output,
            stdout_type=StdoutType.MACHINE_READABLE,
        )

        self._format_services_status(output)


class SystemCli(CommandGroup):
    name = "system"

    aliases = ["sys"]

    short_help = SHORT_HELP_SYSTEM

    help = HELP_SYSTEM

    @inject
    def __init__(self, system_status: SystemStatus) -> None:
        super().__init__()
        self.add_commands(
            [
                system_status,
            ]
        )
