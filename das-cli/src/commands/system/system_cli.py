import threading
import time
import os

import click
from injector import inject

from common import (
    Command,
    CommandGroup,
    Settings,
    StdoutType,
    CommandOption
)
from common.container_manager.system_containers_manager import (
    SystemContainersManager,
)
from common.systemutils.sys_info import (
    SystemInfoExtractor,
)
from common.utils import print_table

from .system_docs import (
    HELP_STATUS,
    HELP_SYSTEM,
    SHORT_HELP_STATUS,
    SHORT_HELP_SYSTEM,
)


class SystemStatus(Command):

    name = "status"

    aliases = ["st", "stat"]

    short_help = SHORT_HELP_STATUS

    help = HELP_STATUS

    params = [
        CommandOption(
            ["--stream", "-s"],
            help = "Shows system status in a constant stream mode, updating each second.",
            default = False,
            required = False
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        system_containers_manager: SystemContainersManager,
        sysinfo_extractor: SystemInfoExtractor,
    ) -> None:

        self._system_containers_manager = system_containers_manager
        self._sysinfo = sysinfo_extractor
        self._settings = settings

        super().__init__()

    def _collect_snapshot(self) -> dict:

        machine_info = {
            "CPUInfo": self._sysinfo.get_cpu_info(),
            "MemoryInfo": self._sysinfo.get_memory_info(),
            "DisksInfo": self._sysinfo.get_disks_info(),
        }

        service_output = (
            self._system_containers_manager
            .get_services_status()
        )

        return {
            "machineInfo": machine_info,
            "serviceInfo": service_output,
        }

    def _run_stream(self) -> None:
        latest_machine = {}
        latest_services = {}

        lock = threading.Lock()

        def machine_loop():

            while True:

                try:

                    data = {
                        "CPUInfo": self._sysinfo.get_cpu_info(),
                        "MemoryInfo": self._sysinfo.get_memory_info(),
                        "DisksInfo": self._sysinfo.get_disks_info(),
                    }

                    with lock:
                        latest_machine.clear()
                        latest_machine.update(data)

                except Exception as e:
                    print(f"[machine_loop] {e}")

                time.sleep(1)

        def docker_loop():

            while True:

                try:
                    data = (
                        self._system_containers_manager
                        .get_services_status()
                    )
                    with lock:
                        latest_services.clear()
                        latest_services.update(data)

                except Exception as e:
                    print(f"[docker_loop] {e}")

                time.sleep(2)

        threading.Thread(
            target=machine_loop,
            daemon=True,
        ).start()

        threading.Thread(
            target=docker_loop,
            daemon=True,
        ).start()

        try:

            while True:
                with lock:
                    system_info = {
                        "machineInfo": dict(latest_machine),
                        "serviceInfo": dict(latest_services),
                    }

                os.system("clear")
                self._format_info_for_display(system_info)
                time.sleep(1)

        except KeyboardInterrupt:
            return

    def _format_info_for_display(
        self,
        system_info: dict,
    ) -> None:

        machines = system_info.get("machineInfo", {})
        services = system_info.get("serviceInfo", {})

        cpu_info = machines.get("CPUInfo", {})
        memory_info = machines.get("MemoryInfo", {})
        disks_info = machines.get("DisksInfo", [])

        self.stdout("MACHINE INFO\n")

        machine_rows = [
            {
                "CPU (%)": cpu_info.get("cpuUsage", 0),
                "CPU CORES": cpu_info.get("cpuTotalCores", 0),
                "MEM USED (MB)": memory_info.get("usedMemory", 0),
                "MEM TOTAL (MB)": memory_info.get("totalMemory", 0),
            }
        ]

        print_table(
            machine_rows,
            columns=[
                "CPU (%)",
                "CPU CORES",
                "MEM USED (MB)",
                "MEM TOTAL (MB)",
            ],
            stdout=self.stdout,
        )

        self.stdout("\nDISKS\n")

        disk_rows = []

        for disk in disks_info:

            disk_rows.append(
                {
                    "DEVICE": disk.get("disk_device", "-"),
                    "MOUNT": disk.get("disk_mntpoint", "-"),
                    "USED (MB)": disk.get("disk_used_space", 0),
                    "TOTAL (MB)": disk.get("disk_total_space", 0),
                }
            )

        print_table(
            disk_rows,
            columns=[
                "DEVICE",
                "MOUNT",
                "USED (MB)",
                "TOTAL (MB)",
            ],
            stdout=self.stdout,
        )

        self.stdout("\nSERVICES\n")

        container_rows = []

        for _, info in services.items():

            container_rows.append(
                {
                    "CONTAINER NAME": info.get("container_name", "-"),
                    "CONTAINER INFO": info.get("image", "-"),
                    "PORT": info.get("port", "-"),
                    "AGE": info.get("age", "-"),
                    "CPU (%)": info.get("cpu_percent", 0),
                    "MEMORY(MB)": info.get("memory_mb", 0),
                    "CONTAINER STATUS": info.get("status", "-"),
                    "SERVICE HEALTH": info.get("service_health", "-"),
                }
            )

        print_table(
            container_rows,
            columns=[
                "CONTAINER NAME",
                "CONTAINER INFO",
                "PORT",
                "AGE",
                "CPU (%)",
                "MEMORY(MB)",
                "CONTAINER STATUS",
                "SERVICE HEALTH",
            ],
            stdout=self.stdout,
        )

    def run(
        self,
        stream: bool = False,
    ) -> None:

        self._settings.validate_configuration_file()

        if stream:
            self._run_stream()
            return

        system_info = self._collect_snapshot()

        self.stdout(
            system_info,
            stdout_type=StdoutType.MACHINE_READABLE,
        )

        self._format_info_for_display(system_info)


class SystemCli(CommandGroup):

    name = "system"

    aliases = ["sys"]

    short_help = SHORT_HELP_SYSTEM

    help = HELP_SYSTEM

    @inject
    def __init__(
        self,
        system_status: SystemStatus,
    ) -> None:

        super().__init__()

        self.add_commands(
            [
                system_status,
            ]
        )