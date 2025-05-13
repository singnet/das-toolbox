from injector import inject
from collections import defaultdict

from common import Command, CommandGroup, StdoutSeverity, CommandOption
from common.utils import get_hardware_fingerprint
from common.exceptions import InstanceNotRegisteredError, InvalidRequestError
from .port_service import PortService


class PortRelease(Command):
    name = "release"

    short_help = ""

    help = ""

    params = [
        CommandOption(
            ["--port", "-p"],
            help="",
            type=int,
            required=True,
        )
    ]

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def run(self, port: int):
        try:
            result = self._port_service.release(port_number=port)

            port_number = result["port"]["port_number"]

            self.stdout(
                f"Successfully released port {port_number}",
                severity=StdoutSeverity.SUCCESS,
            )
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortReserve(Command):
    name = "reserve"

    short_help = ""

    help = ""

    @inject
    def __init__(self, port_service: PortService) -> None:
        super().__init__()
        self._port_service = port_service

    def run(self):
        try:
            result = self._port_service.reserve()

            port_number = result["port"]["port_number"]

            self.stdout(
                f"Reserved port {port_number}",
                severity=StdoutSeverity.SUCCESS,
            )
        except (InstanceNotRegisteredError, InvalidRequestError) as e:
            self.stdout(
                e.message,
                severity=StdoutSeverity.ERROR,
            )


class PortHistory(Command):
    name = "history"

    short_help = ""

    help = ""

    params = [
        CommandOption(
            ["--is-reserved"],
            help="",
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
                status = bind['released_at'] or "IN USE"
                instance_ports[key].append(f"{port['port_number']} ({status})")

        for instance, ports in instance_ports.items():
            self.stdout(f"{instance}")
            for p in ports:
                self.stdout(f"  └─ Port: {p}")
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

    short_help = ""

    help = ""

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
