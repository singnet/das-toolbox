from typing import Optional
from injector import inject
from collections import defaultdict

from common import Command, CommandGroup, StdoutSeverity, CommandOption
from common.utils import get_hardware_fingerprint
from common.exceptions import InstanceNotRegisteredError, InvalidRequestError
from .port_service import PortService


class PortRelease(Command):
    name = "release"

    short_help = "Release a previously reserved port."

    help = (
        "Releases a port that was previously reserved by this instance.\n\n"
        "This tells the API that the port is no longer in use and can be reused by other instances.\n"
        "It is recommended to release ports once your application stops using them to maintain an accurate registry.\n\n"
        "Required option:\n"
        "  -p, --port  Port number to release\n\n"
        "Note: The instance must be registered and own the port to successfully release it."
    )

    params = [
        CommandOption(
            ["--port", "-p"],
            help="",
            type=int,
            required=False,
        ),
        CommandOption(
            ["--range", "-r"],
            help=(
                "Release a previously reserved range of ports. Must be in the format START:END, "
                "as returned by the reserve command. Example: --range 12000:12099."
            ),
            type=str,
            required=False,
        ),
    ]

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def _release_port(self, port: int) -> str:
        result = self._port_service.release_port(port_number=port)

        return result["start_port"]

    def _release_port_range(self, port_range: str) -> str:
        start_port, end_port = map(int, port_range.split(":"))

        result = self._port_service.release_port_range(
            start_port=start_port,
            end_port=end_port,
        )

        return f"{result['start_port']}:{result['end_port']}"

    def run(self, port: Optional[int], range: Optional[str]):
        try:
            if not port and not range:
                raise InvalidRequestError(
                    "You must specify either a port number with --port or a range with --range.",
                    payload={
                        "port": port,
                        "range": range,
                    },
                )

            port_number = (
                self._release_port(port)
                if port
                else self._release_port_range(port_range=range)
            )

            self.stdout(
                port_number,
                severity=StdoutSeverity.SUCCESS,
            )
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortReserve(Command):
    name = "reserve"

    short_help = "Reserve a new available port for the current instance."

    help = (
        "Requests and reserves a new available port for the current machine instance.\n\n"
        "This command contacts the API to allocate an unused port and binds it to this instance.\n"
        "It is useful when you want to ensure port exclusivity for an application or service running on this host.\n\n"
        "Note: The instance must already be registered using the `instance join` command."
    )

    params = [
        CommandOption(
            ["--range"],
            help="Reserve a range of consecutive ports. The output will be in the format START:END",
            type=int,
            required=False,
        )
    ]

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def run(self, range: Optional[int]):
        try:
            result = self._port_service.reserve(range)

            if range:
                port_number = f"{result['start_port']}:{result['end_port']}"
            else:
                port_number = result["start_port"]

            self.stdout(
                port_number,
                severity=StdoutSeverity.SUCCESS,
            )
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortHistory(Command):
    name = "history"

    short_help = "Show history of reserved or released ports."

    help = (
        "Displays the history of ports that have been reserved by the current instance.\n\n"
        "You can use the `--is-reserved` flag to filter by active (default) or released ports.\n\n"
        "Output includes the port number, release status, and a grouping by instance for clarity.\n\n"
        "Options:\n"
        "  --is-reserved     Show only currently reserved ports (default: True)"
    )

    params = [
        CommandOption(
            ["--is-reserved"],
            help="Filter to show only currently reserved ports. Defaults to True.",
            type=bool,
            is_flag=True,
            default=True,
        )
    ]

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def _show_pretty_result(self, result):
        instance_ports = defaultdict(list)

        for port in result:
            for bind in port["bindings"]:
                key = f"{bind['instance']['name']} ({bind['instance']['id'][:12]}...)"
                status = bind["released_at"] or "IN USE"
                port_number = (
                    bind["start_port"]
                    if bind["start_port"] == bind["end_port"]
                    else f"{bind['start_port']}:{bind['end_port']}"
                )
                instance_ports[key].append(f"{port_number} ({status})")

        for instance, ports in instance_ports.items():
            self.stdout(f"{instance}")
            for p in ports:
                port_type = "Range" if ":" in p else "Port"
                self.stdout(f"  └─ {port_type}: {p}")
            self.stdout("\n")

    def run(self, is_reserved: bool):
        try:
            params = {
                "is_reserved": is_reserved,
                "instance_id": get_hardware_fingerprint(),
            }

            result = self._port_service.list(params)
            self._show_pretty_result(result)
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortCli(CommandGroup):
    name = "port"

    short_help = "Manage reserved ports for the current machine instance."

    help = (
        "This command group provides tools to manage port reservations linked to machine instances.\n\n"
        "Available commands:\n"
        "  reserve   - Reserve a new available port for the current instance.\n"
        "  release   - Release a specific port no longer in use.\n"
        "  history   - List all ports reserved (or released) by this instance.\n\n"
        "Use `--help` with each command to get more detailed usage information."
    )

    @inject
    def __init__(
        self,
        port_release: PortRelease,
        port_reserve: PortReserve,
        port_history: PortHistory,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                port_release.command,
                port_reserve.command,
                port_history.command,
            ]
        )
