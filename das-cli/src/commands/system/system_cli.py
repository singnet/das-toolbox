import os
import threading
import time

from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutType
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
            help="Shows system status in a constant stream mode, updating each second.",
            default=False,
            required=False,
            is_flag=True,
        ),
        CommandOption(
            ["--cooldown", "-c"],
            help="Sets how many seconds of cooldown before updating the metrics again.",
            default=2,
            required=False,
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

    def run(
        self,
        stream: bool = False,
        cooldown: int = 2,
    ) -> None:

        self._settings.validate_configuration_file()

        if stream:

            if cooldown < 2:
                raise ValueError("Cooldown value cannot be smaller than 2 seconds")

            self._run_stream(cooldown)
            return

        # Solo snapshot
        system_info = self._collect_snapshot()
        self.stdout(
            system_info,
            stdout_type=StdoutType.MACHINE_READABLE,
        )

        self._format_info_for_display(system_info)

    def _collect_snapshot(self) -> dict:

        machine_info = {
            "CPUInfo": self._sysinfo.get_cpu_info(interval=2),
            "MemoryInfo": self._sysinfo.get_memory_info(),
            "DisksInfo": self._sysinfo.get_disks_info(),
        }

        service_output = self._system_containers_manager.get_services_status()

        return {
            "machineInfo": machine_info,
            "serviceInfo": service_output,
        }

    def _format_info_for_display(
        self,
        system_info: dict,
    ) -> None:

        machines = system_info.get("machineInfo", {})
        services = system_info.get("serviceInfo", {})

        cpu_info = machines.get("CPUInfo", {})
        memory_info = machines.get("MemoryInfo", {})
        disks_info = machines.get("DisksInfo", [])

        self.stdout("MACHINE INFO:\n")

        machine_rows = [
            {
                "CPU (Machine load / %)": cpu_info.get("cpuUsage", 0),
                "CPU CORES": cpu_info.get("cpuTotalCores", 0),
                "MEM USED (GB)": memory_info.get("usedMemory", 0),
                "MEM TOTAL (GB)": memory_info.get("totalMemory", 0),
            }
        ]

        print_table(
            machine_rows,
            columns=[
                "CPU (Machine load / %)",
                "CPU CORES",
                "MEM USED (GB)",
                "MEM TOTAL (GB)",
            ],
            stdout=self.stdout,
        )

        self.stdout("\nDISKS:\n")

        disk_rows = []

        for disk in disks_info:

            disk_rows.append(
                {
                    "DEVICE": disk.get("disk_device", "-"),
                    "MOUNT": disk.get("disk_mntpoint", "-"),
                    "USED (GB)": disk.get("disk_used_space", 0),
                    "TOTAL (GB)": disk.get("disk_total_space", 0),
                }
            )

        print_table(
            disk_rows,
            columns=[
                "DEVICE",
                "MOUNT",
                "USED (GB)",
                "TOTAL (GB)",
            ],
            stdout=self.stdout,
        )

        self.stdout("\nSERVICES:\n")

        container_rows = []

        for _, info in services.items():

            container_rows.append(
                {
                    "CONTAINER NAME": info.get("container_name", "-"),
                    "CONTAINER INFO": info.get("image", "-"),
                    "PORT": info.get("port", "-"),
                    "AGE": info.get("age", "-"),
                    "CPU (Container %)": info.get("cpu_percent", 0),
                    "MEMORY(GB)": info.get("memory_mb", 0),
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
                "CPU (Container %)",
                "MEMORY(GB)",
                "CONTAINER STATUS",
                "SERVICE HEALTH",
            ],
            stdout=self.stdout,
        )

    def _run_stream(self, cooldown) -> None:
        latest_machine: dict[str, str] = {}
        latest_services: dict[str, str] = {}

        lock = threading.Lock()

        def machine_loop():

            while True:

                try:

                    data = {
                        "CPUInfo": self._sysinfo.get_cpu_info(cooldown),
                        "MemoryInfo": self._sysinfo.get_memory_info(),
                        "DisksInfo": self._sysinfo.get_disks_info(),
                    }

                    with lock:
                        latest_machine.clear()
                        latest_machine.update(data)


                except Exception as e:
                    print(f"[machine_loop] {e}")

        def docker_loop():

            while True:
                try:
                    data = self._system_containers_manager.get_services_status()
                    with lock:
                        latest_services.clear()
                        latest_services.update(data)
                except Exception as e:
                    print(f"[docker_loop] {e}")

        threading.Thread(
            target=docker_loop,
            daemon=True,
        ).start()

        threading.Thread(
            target=machine_loop,
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

                self.stdout(system_info, stdout_type=StdoutType.MACHINE_READABLE, stream_mode=True)
                self._format_info_for_display(system_info)
                time.sleep(cooldown)

        except KeyboardInterrupt:
            return


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
